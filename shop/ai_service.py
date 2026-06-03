import json
import re
from typing import Any, Generator, Iterator, Optional

import requests
from django.conf import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

PRODUCT_CATEGORIES = [
    "Bento Candles",
    "Scented Candles",
    "Decorative Candles",
    "Gift Collections",
]

CHAT_SYSTEM_PROMPT = """You are Mimosa Copilot — a sharp assistant in the Django admin of Mimosa Atelier (luxury artisan candles).

RULES:
1. Infer intent: greeting, question, brainstorm, translation, or product copy. Do NOT default to long marketing text.
2. Short questions → short clear answers. Greetings → 1–2 warm sentences.
3. Product descriptions only when asked: elegant French boutique copy, <br> for breaks, no markdown asterisks.
4. Reply in the user's language unless they ask otherwise.
5. Never mention being an AI or Groq."""

FORM_FILL_SYSTEM_PROMPT = """You fill the Django admin "Add/Change Product" form for Mimosa Atelier (luxury candles).

Return ONLY one JSON object (no markdown, no extra text) with these keys — use empty string "" if unknown:
{
  "title": "product name",
  "description": "HTML allowed: use <br> for line breaks, French luxury tone if appropriate",
  "category": "exactly one of: Bento Candles | Scented Candles | Decorative Candles | Gift Collections",
  "hs_code": "e.g. 340600",
  "price": "decimal as string e.g. 24.00",
  "stock": "integer as string",
  "scent": "fragrance notes",
  "wick": "wick type",
  "weight": "display weight e.g. 200 g",
  "weight_grams": "integer grams for shipping",
  "burn_time": "e.g. 40 h",
  "composition": "wax/materials",
  "form_capacity": "vessel size if relevant",
  "wax_type": "e.g. soy, beeswax blend"
}

Infer all fields from the user's message. Be realistic for a candle shop."""


def _api_key() -> str:
    api_key = (getattr(settings, "GROQ_API_KEY", None) or "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it in Render → Environment."
        )
    return api_key


def _groq_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json; charset=utf-8",
    }


def wants_product_form_fill(prompt_text: str, *, on_product_form: bool) -> bool:
    if not on_product_form:
        return False
    p = prompt_text.lower()
    triggers = (
        "заполни",
        "заповни",
        "заполн",
        "fill",
        "заповн",
        "поля",
        "форм",
        "рядк",
        "строк",
        "form",
        "add product",
        "добав",
        "створи товар",
        "создай товар",
        "новий товар",
        "новый товар",
    )
    return any(t in p for t in triggers)


def _chat_payload(
    prompt_text: str,
    *,
    stream: bool,
    system_prompt: str,
    json_mode: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text},
        ],
        "temperature": 0.55 if json_mode else 0.65,
        "max_tokens": 1200 if json_mode else 1024,
        "stream": stream,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    return payload


def _raise_for_groq_error(response: requests.Response) -> None:
    if response.ok:
        return
    try:
        err_body = response.json()
        err_msg = err_body.get("error", {}).get("message", response.text)
    except ValueError:
        err_msg = response.text
    raise RuntimeError(f"Groq API error ({response.status_code}): {err_msg}")


def _parse_sse_line(line: bytes) -> Optional[str]:
    if not line.startswith(b"data: "):
        return None
    data_str = line[6:].strip()
    if data_str == b"[DONE]":
        return None
    try:
        chunk = json.loads(data_str.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    delta = chunk["choices"][0]["delta"].get("content")
    return delta or None


def stream_chat_completion(prompt_text: str) -> Iterator[str]:
    """Yield UTF-8 text deltas from Groq streaming API."""
    with requests.post(
        GROQ_API_URL,
        headers=_groq_headers(),
        json=_chat_payload(prompt_text, stream=True, system_prompt=CHAT_SYSTEM_PROMPT),
        stream=True,
        timeout=120,
    ) as response:
        _raise_for_groq_error(response)

        for raw_line in response.iter_lines(decode_unicode=False):
            if not raw_line:
                continue
            delta = _parse_sse_line(raw_line)
            if delta:
                yield delta


def generate_chat_reply(prompt_text: str) -> str:
    response = requests.post(
        GROQ_API_URL,
        headers=_groq_headers(),
        json=_chat_payload(
            prompt_text,
            stream=False,
            system_prompt=CHAT_SYSTEM_PROMPT,
        ),
        timeout=120,
    )
    _raise_for_groq_error(response)
    data = response.json()
    content: Optional[str] = data["choices"][0]["message"]["content"]
    return (content or "").strip()


def _normalize_form_fields(raw: dict[str, Any]) -> dict[str, str]:
    allowed = {
        "title",
        "description",
        "category",
        "hs_code",
        "price",
        "stock",
        "scent",
        "wick",
        "weight",
        "weight_grams",
        "burn_time",
        "composition",
        "form_capacity",
        "wax_type",
    }
    result: dict[str, str] = {}
    for key in allowed:
        if key not in raw:
            continue
        value = raw[key]
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        if key == "category" and text not in PRODUCT_CATEGORIES:
            for choice in PRODUCT_CATEGORIES:
                if choice.lower() == text.lower():
                    text = choice
                    break
            else:
                text = "Scented Candles"
        result[key] = text
    return result


def generate_product_form_fields(prompt_text: str) -> dict[str, Any]:
    response = requests.post(
        GROQ_API_URL,
        headers=_groq_headers(),
        json=_chat_payload(
            prompt_text,
            stream=False,
            system_prompt=FORM_FILL_SYSTEM_PROMPT,
            json_mode=True,
        ),
        timeout=120,
    )
    _raise_for_groq_error(response)
    data = response.json()
    content: Optional[str] = data["choices"][0]["message"]["content"]
    if not content:
        raise RuntimeError("Empty response from Groq.")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            raise RuntimeError("Model did not return valid JSON for form fill.")
        parsed = json.loads(match.group(0))

    fields = _normalize_form_fields(parsed)
    if not fields:
        raise RuntimeError("No product fields were generated.")

    title = fields.get("title", "New candle")
    summary = (
        f"Готово: заповнено {len(fields)} полів для «{title}». "
        "Перевірте форму та збережіть товар."
    )
    return {"form_fields": fields, "message": summary}


def _sse_bytes(payload: dict[str, Any]) -> bytes:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")


def stream_sse_events(prompt_text: str) -> Generator[bytes, None, None]:
    """Server-Sent Events (UTF-8 bytes) for the admin Copilot frontend."""
    try:
        for delta in stream_chat_completion(prompt_text):
            yield _sse_bytes({"delta": delta})
        yield _sse_bytes({"done": True})
    except Exception as exc:
        yield _sse_bytes({"error": str(exc)})


# Backwards compatibility
def generate_premium_description(prompt_text: str) -> str:
    return generate_chat_reply(prompt_text)

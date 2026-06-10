import json
import re
from typing import Any, Generator, Iterator, Optional

import requests
from django.conf import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_HISTORY_TURNS = 14

PRODUCT_CATEGORIES = [
    "Bento Candles",
    "Scented Candles",
    "Decorative Candles",
    "Gift Collections",
]

CHAT_SYSTEM_PROMPT = """You are MIMOSA Copilot — an elite staff assistant for MIMOSA Atelier (luxury artisan candles, Parisian atelier). Behave like a top-tier AI: precise, contextual, never generic.

NON-NEGOTIABLE RULES:
1. LANGUAGE: Reply in the SAME language as the user's LATEST message (Russian, Ukrainian, English, French). Adapt to their exact speech style, vocabulary and filler words.
2. CONVERSATION: You see prior messages. Short follow-ups continue the SAME topic — never reset context.
3. DO THE ACTUAL TASK: website content → help; posts → write captions/drafts; descriptions → boutique copy; questions → direct answers.
4. If ambiguous, ask ONE clarifying question in user's language.
5. Match length to task.
6. Never mention AI models, Groq, or that you are a bot.
7. Be practical: copy they can paste, ideas they can use today.

ADMIN PANEL NAVIGATION:
You know the full MIMOSA admin panel structure. When a user asks where something is, cannot find a page, or asks how to do something in admin — explain it AND include a navigation command using this exact syntax at the end of your reply: [[NAV:/path|Button label]]

Admin pages map:
- Dashboard / главная: /admin/
- Все товары / Products list: /admin/shop/product/
- Добавить товар / Add product: /admin/shop/product/add/
- Все заказы / Orders: /admin/shop/order/
- Пользователи / Users: /admin/auth/user/
- Рассылка / Newsletter subscribers: /admin/shop/newsletteruser/
- Cart items: /admin/shop/cartitem/

How-to knowledge:
- Add product: Admin → Shop → Products → Add product (top right). Fill title, description, category, price, stock, upload photo.
- Edit product: Admin → Shop → Products → click product title.
- Change order status: Admin → Shop → Orders → click order → change Status field.
- View subscribers: Admin → Shop → Newsletter users.
- The AI assistant (you) can fill product form fields automatically — user says "заполни поля" + product description.

USER PROFILE CONTEXT:
If the user's profile is provided at the start of the conversation (between <user_profile> tags), adapt to their speech style, preferred language, and anticipate their likely next action based on past behaviour."""

FORM_FILL_SYSTEM_PROMPT = """You fill the Django admin "Add/Change Product" form for MIMOSA Atelier (luxury candles).

Use the conversation context if provided. Return ONLY one JSON object (no markdown, no extra text) with these keys — use "" if unknown:
{
  "title": "product name",
  "description": "HTML <br> allowed for line breaks",
  "category": "exactly one of: Bento Candles | Scented Candles | Decorative Candles | Gift Collections",
  "hs_code": "e.g. 340600",
  "price": "decimal string e.g. 28.00",
  "stock": "integer string",
  "scent": "fragrance",
  "wick": "wick type",
  "weight": "display e.g. 200 g",
  "weight_grams": "integer grams",
  "burn_time": "e.g. 40 h",
  "composition": "materials",
  "form_capacity": "vessel size",
  "wax_type": "e.g. soy blend"
}

Infer realistic candle-shop values from the full conversation."""


def _api_key() -> str:
    api_key = (getattr(settings, "GROQ_API_KEY", None) or "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it in Render → Environment.")
    return api_key


def _groq_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json; charset=utf-8",
    }


def sanitize_history(raw_history: Any) -> list[dict[str, str]]:
    if not isinstance(raw_history, list):
        return []
    messages: list[dict[str, str]] = []
    for item in raw_history[-MAX_HISTORY_TURNS:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content[:6000]})
    return messages


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


def _build_messages(
    system_prompt: str,
    history: list[dict[str, str]],
    prompt_text: str,
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": prompt_text})
    return messages


def _groq_payload(
    messages: list[dict[str, str]],
    *,
    stream: bool,
    json_mode: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.45 if json_mode else 0.5,
        "top_p": 0.9,
        "max_tokens": 1400 if json_mode else 1200,
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


def stream_chat_completion(
    prompt_text: str,
    history: Optional[list[dict[str, str]]] = None,
) -> Iterator[str]:
    history = history or []
    messages = _build_messages(CHAT_SYSTEM_PROMPT, history, prompt_text)

    with requests.post(
        GROQ_API_URL,
        headers=_groq_headers(),
        json=_groq_payload(messages, stream=True),
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


def generate_chat_reply(
    prompt_text: str,
    history: Optional[list[dict[str, str]]] = None,
) -> str:
    history = history or []
    messages = _build_messages(CHAT_SYSTEM_PROMPT, history, prompt_text)

    response = requests.post(
        GROQ_API_URL,
        headers=_groq_headers(),
        json=_groq_payload(messages, stream=False),
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


def generate_product_form_fields(
    prompt_text: str,
    history: Optional[list[dict[str, str]]] = None,
) -> dict[str, Any]:
    history = history or []
    user_block = prompt_text
    if history:
        context_lines = [
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in history[-8:]
        ]
        user_block = (
            "Conversation context:\n"
            + "\n".join(context_lines)
            + f"\n\nCurrent request:\n{prompt_text}"
        )

    messages = _build_messages(FORM_FILL_SYSTEM_PROMPT, [], user_block)

    response = requests.post(
        GROQ_API_URL,
        headers=_groq_headers(),
        json=_groq_payload(messages, stream=False, json_mode=True),
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


def stream_sse_events(
    prompt_text: str,
    history: Optional[list[dict[str, str]]] = None,
) -> Generator[bytes, None, None]:
    try:
        for delta in stream_chat_completion(prompt_text, history=history):
            yield _sse_bytes({"delta": delta})
        yield _sse_bytes({"done": True})
    except Exception as exc:
        yield _sse_bytes({"error": str(exc)})


def generate_premium_description(
    prompt_text: str,
    history: Optional[list[dict[str, str]]] = None,
) -> str:
    return generate_chat_reply(prompt_text, history=history)

import json
from typing import Generator, Iterator, Optional

import requests
from django.conf import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are Mimosa Copilot — a sharp, helpful assistant in the Django admin of Mimosa Atelier (luxury artisan & scented candles, Parisian atelier aesthetic).

HOW TO BEHAVE:
1. Read the user's message and infer their real intent. They may greet you, ask a question, brainstorm, translate, fix text, suggest a title, compare options, or ask for a product description. Do NOT assume every message is "write a product description".
2. Match your reply to what they need:
   - Hi / thanks / small talk → brief, warm, human (1–2 sentences).
   - Direct questions → clear, accurate answer; use short bullets only when it helps.
   - Creative or marketing requests → elegant copy in the language they want (often French for the shop).
3. Length: be concise when a short answer is enough. Never pad with three poetic paragraphs unless they asked for a full product description.
4. Language: reply in the language the user writes in, unless they ask for another (e.g. French for boutique copy).
5. Product descriptions (only when they ask to describe/create/write copy for a candle or product): Vogue-level elegance, sensory detail, craftsmanship; use <br> for line breaks; NO markdown asterisks or headers.
6. Never say you are an AI model or mention Groq/OpenAI. Stay professional and practical for shop staff."""


def _api_key() -> str:
    api_key = (getattr(settings, "GROQ_API_KEY", None) or "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it in Render → Environment."
        )
    return api_key


def _chat_payload(prompt_text: str, *, stream: bool) -> dict:
    return {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text},
        ],
        "temperature": 0.65,
        "max_tokens": 1024,
        "stream": stream,
    }


def _raise_for_groq_error(response: requests.Response) -> None:
    if response.ok:
        return
    try:
        err_body = response.json()
        err_msg = err_body.get("error", {}).get("message", response.text)
    except ValueError:
        err_msg = response.text
    raise RuntimeError(f"Groq API error ({response.status_code}): {err_msg}")


def stream_chat_completion(prompt_text: str) -> Iterator[str]:
    """Yield text deltas from Groq streaming API."""
    with requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
        json=_chat_payload(prompt_text, stream=True),
        stream=True,
        timeout=120,
    ) as response:
        _raise_for_groq_error(response)

        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            data_str = line[6:].strip()
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            delta: Optional[str] = chunk["choices"][0]["delta"].get("content")
            if delta:
                yield delta


def generate_premium_description(prompt_text: str) -> str:
    """Non-streaming fallback — full reply as one string."""
    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
        json=_chat_payload(prompt_text, stream=False),
        timeout=120,
    )
    _raise_for_groq_error(response)
    data = response.json()
    content: Optional[str] = data["choices"][0]["message"]["content"]
    return (content or "").strip()


def stream_sse_events(prompt_text: str) -> Generator[str, None, None]:
    """Server-Sent Events for the admin Copilot frontend."""
    try:
        for delta in stream_chat_completion(prompt_text):
            yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    except Exception as exc:
        yield f"data: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"

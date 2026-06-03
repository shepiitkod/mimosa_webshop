from typing import Optional

import requests
from django.conf import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# gemma2-9b-it was retired on Groq (Oct 2025); use their recommended fast replacement.
GROQ_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = (
    "You are an elite French copywriter for 'Mimosa Atelier', a luxury brand creating "
    "artisanal, custom, and scented candles. Transform the user's prompt into a beautiful, "
    "premium, and poetic product description in French. Emphasize craftsmanship and sensory "
    "experience. Use HTML <br> tags for layout, but NO markdown asterisks. "
    "Tone: Vogue magazine, elegant."
)


def generate_premium_description(prompt_text: str) -> str:
    api_key = (getattr(settings, "GROQ_API_KEY", None) or "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it in Render → Environment."
        )

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0.85,
            "max_tokens": 400,
        },
        timeout=60,
    )

    if not response.ok:
        try:
            err_body = response.json()
            err_msg = err_body.get("error", {}).get("message", response.text)
        except ValueError:
            err_msg = response.text
        raise RuntimeError(f"Groq API error ({response.status_code}): {err_msg}")

    data = response.json()
    content: Optional[str] = data["choices"][0]["message"]["content"]
    return (content or "").strip()

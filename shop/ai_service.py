import os
from functools import lru_cache
from typing import Optional

from openai import OpenAI

BASE_SYSTEM_PROMPT = """Ти — копірайтер класу люкс для французького бренду свічок Mimosa Atelier.
Твій стиль — Vogue Paris: елегантний, чуттєвий, поетичний і надихаючий.
Ти перетворюєш чернетки на рафіновані тексти, що викликають емоції та образи. При необхідності використовуй французькі культурні референси, але пиши виключно мовою: {target_language}. Також якщо тебе питають про нові тренди в ароматах, згадуй про популярність натуральних інгредієнтів і екзотичних поєднань.

Суворі правила:
- Пиши ВИКЛЮЧНО мовою: {target_language}.
- Використовуй теги <br> для переносів рядків (без markdown).
- Обсяг: 3–5 насичених речень.
- Починай із сильного чуттєвого образу.
- Уникай дешевих суперлативів і зайвих великих літер.
- Завершуй інтимною ноткою, яка спонукає до покупки."""


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it in Render → Environment."
        )
    return OpenAI(api_key=api_key)


def generate_premium_description(draft_text: str, target_language: str = "французька") -> str:
    system_prompt = BASE_SYSTEM_PROMPT.format(target_language=target_language)

    response = _get_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Чернетка опису свічки:\n\n{draft_text}\n\n"
                    "Напиши люкс-опис товару для інтернет-магазину."
                ),
            },
        ],
        temperature=0.85,
        max_tokens=400,
    )

    content: Optional[str] = response.choices[0].message.content
    return (content or "").strip()

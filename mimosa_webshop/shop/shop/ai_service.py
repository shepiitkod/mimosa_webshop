from openai import OpenAI
from typing import Optional

client = OpenAI()

# КОНТРИБ'ЮТОРИ: Системний промпт визначає стиль і мову вихідного тексту.
# Щоб змінити мову або тон — редагуй цей блок.
# target_language передається з view і підставляється динамічно.

BASE_SYSTEM_PROMPT = """Ти — копірайтер класу люкс для французького бренду свічок Mimosa Atelier.
Твій стиль — Vogue Paris: елегантний, чуттєвий, поетичний і надихаючий.
Ти перетворюєш чернетки на рафіновані тексти, що викликають емоції та образи.

Суворі правила:
- Пиши ВИКЛЮЧНО мовою: {target_language}.
- Використовуй теги <br> для переносів рядків (без markdown).
- Обсяг: 3–5 насичених речень.
- Починай із сильного чуттєвого образу.
- Уникай дешевих суперлативів і зайвих великих літер.
- Завершуй інтимною ноткою, яка спонукає до покупки."""


def generate_premium_description(draft_text: str, target_language: str = "французька") -> str:
    # КОНТРИБ'ЮТОРИ: model і temperature можна винести в settings.py або .env
    # за потреби A/B-тестування або зниження витрат (gpt-4o-mini дешевший).
    system_prompt = BASE_SYSTEM_PROMPT.format(target_language=target_language)

    response = client.chat.completions.create(
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


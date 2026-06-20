import hashlib
import json
import re
from typing import Any

import requests
from django.conf import settings

from .models import Product

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
SUPPORTED_LANGS = ("en", "fr", "ua", "ru")
I18N_FIELDS = (
    "title",
    "description",
    "scent",
    "wick",
    "burn_time",
    "composition",
    "form_capacity",
    "wax_type",
)

TRANSLATION_SYSTEM_PROMPT = """You translate MIMOSA Atelier luxury candle product fields for an e-commerce storefront.

Return ONLY one JSON object with keys en, fr, ua, ru. Each language value is an object with the same field keys as the input.

Rules:
- Preserve HTML line breaks (<br>, <br/>) in description exactly where they belong.
- Keep brand name MIMOSA unchanged.
- Use natural boutique copy in each target language.
- If a field is empty in the source, return an empty string for that field in every language.
- Do not add markdown or commentary."""


def _api_key() -> str:
    return (getattr(settings, "GROQ_API_KEY", None) or "").strip()


def _source_payload(product: Product) -> dict[str, str]:
    return {field: (getattr(product, field) or "").strip() for field in I18N_FIELDS}


def _source_hash(payload: dict[str, str]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _fallback_i18n(payload: dict[str, str]) -> dict[str, Any]:
    return {lang: dict(payload) for lang in SUPPORTED_LANGS}


def _normalize_i18n(raw: Any, payload: dict[str, str]) -> dict[str, dict[str, str]]:
    if not isinstance(raw, dict):
        return _fallback_i18n(payload)

    normalized: dict[str, dict[str, str]] = {}
    for lang in SUPPORTED_LANGS:
        lang_data = raw.get(lang, {})
        if not isinstance(lang_data, dict):
            lang_data = {}
        normalized[lang] = {
            field: str(lang_data.get(field, payload.get(field, ""))).strip()
            for field in I18N_FIELDS
        }
    return normalized


def _translate_with_groq(payload: dict[str, str]) -> dict[str, dict[str, str]]:
    api_key = _api_key()
    if not api_key:
        return _fallback_i18n(payload)

    user_prompt = (
        "Translate these candle product fields into English (en), French (fr), "
        "Ukrainian (ua), and Russian (ru):\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json; charset=utf-8",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 2400,
            "response_format": {"type": "json_object"},
        },
        timeout=120,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    if not content:
        raise RuntimeError("Empty translation response from Groq.")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            raise RuntimeError("Groq did not return valid JSON for product translation.")
        parsed = json.loads(match.group(0))

    return _normalize_i18n(parsed, payload)


def product_needs_retranslation(product: Product) -> bool:
    payload = _source_payload(product)
    if not any(payload.values()):
        return False

    stored = product.i18n if isinstance(product.i18n, dict) else {}
    if stored.get("_source_hash") != _source_hash(payload):
        return True

    for lang in SUPPORTED_LANGS:
        lang_data = stored.get(lang)
        if not isinstance(lang_data, dict):
            return True
        for field in I18N_FIELDS:
            if field not in lang_data:
                return True
    return False


def build_product_i18n(product: Product) -> dict[str, Any]:
    payload = _source_payload(product)
    if not any(payload.values()):
        return {}

    translations = _translate_with_groq(payload)
    return {
        "_source_hash": _source_hash(payload),
        **translations,
    }


def sync_product_translations(product: Product, *, force: bool = False) -> bool:
    if not force and not product_needs_retranslation(product):
        return False

    i18n_data = build_product_i18n(product)
    if not i18n_data:
        return False

    Product.objects.filter(pk=product.pk).update(i18n=i18n_data)
    product.i18n = i18n_data
    return True

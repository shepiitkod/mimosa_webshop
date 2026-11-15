"""Fragrance table on the Seconde vie page: filters, sorting and the rows the
template needs. Names and notes stay French; family terms, seasons and
moments get translation keys (translations.js), description / mood come
from Fragrance.i18n."""

import json

from django.templatetags.static import static
from django.utils.html import escape
from django.utils.text import slugify

from .models import Fragrance

SEASONS = [code for code, _ in Fragrance.SEASON_CHOICES]
SEASON_LABELS = dict(Fragrance.SEASON_CHOICES)

INTENSITY_BANDS = (
    ("legere", "Légère", 1, 2),
    ("moyenne", "Moyenne", 3, 3),
    ("intense", "Intense", 4, 5),
)
SORTS = ("nom", "intensite-asc", "intensite-desc")


def term_key(text):
    """translations.js key for a French term (family word, moment)."""
    return "frag-t-" + slugify(text)


def _terms(values):
    return [{"text": v, "key": term_key(v)} for v in values]


def filter_fragrances(fragrances, famille="", intensite="", saison="", tri=""):
    """Return the visible fragrances in display order (works on any iterable
    of Fragrance). Unknown values are ignored."""
    items = [f for f in fragrances if f.is_active]
    if famille in dict(Fragrance.FAMILY_CHOICES):
        items = [f for f in items if f.family_group == famille]
    band = {b[0]: b for b in INTENSITY_BANDS}.get(intensite)
    if band:
        items = [f for f in items if band[2] <= f.intensity <= band[3]]
    if saison in SEASONS:
        items = [f for f in items if saison in (f.seasons or [])]
    if tri == "intensite-asc":
        items.sort(key=lambda f: (f.intensity, f.name.lower()))
    elif tri == "intensite-desc":
        items.sort(key=lambda f: (-f.intensity, f.name.lower()))
    elif tri == "nom":
        items.sort(key=lambda f: f.name.lower())
    return items


def table_context(params):
    """Everything the template needs: every row (hidden ones flagged), the
    filter options and the active values."""
    active = {
        "famille": params.get("famille", ""),
        "intensite": params.get("intensite", ""),
        "saison": params.get("saison", ""),
        "tri": params.get("tri", "") if params.get("tri", "") in SORTS else "",
    }
    every = list(Fragrance.objects.filter(is_active=True))
    visible = filter_fragrances(every, **active)
    visible_ids = {f.id for f in visible}
    ordered = visible + [f for f in every if f.id not in visible_ids]

    rows = []
    for f in ordered:
        if f.image:
            thumb = big = f.image.url
        else:
            base = f.static_image or "assets/images/fragrances/" + f.slug
            thumb = static(base + "-160.webp")
            big = static(base + "-720.webp")
        i18n = {lang: {"description": v.get("description", ""), "mood": v.get("mood", "")} for lang, v in (f.i18n or {}).items()}
        i18n["fr"] = {"description": f.description, "mood": f.mood}
        rows.append(
            {
                "obj": f,
                "hidden": f.id not in visible_ids,
                "family_terms": _terms([t.strip() for t in f.family.split("·") if t.strip()]),
                "seasons": [{"code": s, "label": SEASON_LABELS[s], "key": "frag-season-" + s} for s in SEASONS if s in (f.seasons or [])],
                "all_seasons": f.all_seasons,
                "moments": _terms(f.moments or []),
                "dots": range(1, 6),
                "thumb": thumb,
                "big": big,
                "i18n_json": escape(json.dumps(i18n, ensure_ascii=False)),
            }
        )

    return {
        "fragrance_rows": rows,
        "fragrance_total": len(every),
        "fragrance_visible": len(visible),
        "frag_families": [{"code": c, "label": l, "key": "frag-group-" + c} for c, l in Fragrance.FAMILY_CHOICES],
        "frag_bands": [{"code": c, "label": l, "key": "frag-band-" + c} for c, l, _, _ in INTENSITY_BANDS],
        "frag_seasons": [{"code": c, "label": SEASON_LABELS[c], "key": "frag-season-" + c} for c in SEASONS],
        "frag_active": active,
        "frag_filtered": any(active.values()),
    }

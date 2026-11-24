"""Import and export the product catalogue as JSON or CSV.

Used by the admin "Import / export" page and by the ``import_products`` /
``export_products`` management commands, so a catalogue can be moved between
databases (e.g. from the old Render database to the Vercel/Neon one) without
re-uploading photos: image fields hold the stored file name (the Cloudinary
public id in production), so the photos keep pointing at the same files.

Accepted input:
* JSON produced by ``manage.py dumpdata`` (any models; only ``shop.product``
  entries are used), or by the export on this page;
* a plain JSON list of product objects;
* CSV with a header row using the Product field names.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from django.core.management.color import no_style
from django.db import connection, transaction

from .models import Product

IMAGE_FIELDS = ("image", "image_2", "image_3", "image_4")
EXPORT_FIELDS = tuple(
    f.name for f in Product._meta.concrete_fields if f.name != "id"
)
_INT_FIELDS = {
    f.name
    for f in Product._meta.concrete_fields
    if f.get_internal_type() in ("PositiveIntegerField", "PositiveSmallIntegerField")
}


@dataclass
class ImportResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def export_products_json() -> str:
    rows = []
    for product in Product.objects.order_by("id"):
        fields = {}
        for name in EXPORT_FIELDS:
            value = getattr(product, name)
            if name in IMAGE_FIELDS:
                value = value.name if value else ""
            elif isinstance(value, Decimal):
                value = str(value)
            fields[name] = value
        rows.append({"model": "shop.product", "pk": product.pk, "fields": fields})
    return json.dumps(rows, ensure_ascii=False, indent=2)


def export_products_csv() -> str:
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(("id", *EXPORT_FIELDS))
    for row in json.loads(export_products_json()):
        values = []
        for name in EXPORT_FIELDS:
            value = row["fields"][name]
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            values.append(value)
        writer.writerow((row["pk"], *values))
    return out.getvalue()


def _parse(raw: str) -> list[tuple[int | None, dict]]:
    """Return (pk, fields) pairs from JSON or CSV text."""
    text = raw.lstrip("﻿").strip()
    if not text:
        return []

    if text[0] in "[{":
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("products") or [data]
        records = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if "fields" in item:  # dumpdata format
                if str(item.get("model", "")).lower() != "shop.product":
                    continue
                records.append((item.get("pk"), dict(item["fields"])))
            else:
                item = dict(item)
                records.append((item.pop("id", None) or item.pop("pk", None), item))
        return records

    records = []
    for row in csv.DictReader(io.StringIO(text)):
        row = {k.strip(): v for k, v in row.items() if k}
        pk = row.pop("id", None) or row.pop("pk", None)
        if row.get("i18n"):
            try:
                row["i18n"] = json.loads(row["i18n"])
            except ValueError:
                row.pop("i18n")
        records.append((pk, row))
    return records


def _clean_fields(fields: dict) -> dict:
    allowed = set(EXPORT_FIELDS)
    clean = {}
    for name, value in fields.items():
        if name not in allowed:
            continue
        if value is None:
            if name in IMAGE_FIELDS:
                value = ""
            elif name in _INT_FIELDS or name == "price":
                continue  # keep the model default
            elif name == "hs_code":
                value = None
            else:
                value = ""
        elif name == "price":
            value = Decimal(str(value).replace(",", ".").strip() or "0")
        elif name in _INT_FIELDS:
            if str(value).strip() == "":
                continue
            value = int(float(str(value).replace(",", ".")))
        elif name == "i18n":
            value = value if isinstance(value, dict) else {}
        else:
            value = str(value).strip() if name not in IMAGE_FIELDS else str(value).strip()
        clean[name] = value
    return clean


def _reset_sequence() -> None:
    sql = connection.ops.sequence_reset_sql(no_style(), [Product])
    if sql:
        with connection.cursor() as cursor:
            for statement in sql:
                cursor.execute(statement)


def import_products(raw: str, *, update_existing: bool = True) -> ImportResult:
    """Create or update products from JSON/CSV text.

    A product is matched to an existing one by title (case-insensitive). New
    products keep their original id when it is free, so old product links keep
    working. Saving bypasses image re-processing and auto-translation
    (``raw=True``) because the data is already final; translations included
    in the file are kept.
    """
    result = ImportResult()
    try:
        records = _parse(raw)
    except (ValueError, csv.Error) as exc:
        result.errors.append(f"Не удалось прочитать файл: {exc}")
        return result

    if not records:
        result.errors.append("В файле не найдено ни одного товара (shop.product).")
        return result

    existing_by_title = {
        p.title.strip().lower(): p for p in Product.objects.all()
    }

    with transaction.atomic():
        for index, (pk, fields) in enumerate(records, start=1):
            try:
                clean = _clean_fields(fields)
            except (InvalidOperation, ValueError, TypeError) as exc:
                result.errors.append(f"Строка {index}: неверное значение ({exc}).")
                continue

            title = (clean.get("title") or "").strip()
            if not title:
                result.errors.append(f"Строка {index}: нет названия, пропущено.")
                continue

            product = existing_by_title.get(title.lower())
            if product is not None:
                if not update_existing:
                    result.skipped += 1
                    continue
                for name, value in clean.items():
                    setattr(product, name, value)
                product.save_base(raw=True)
                result.updated += 1
                continue

            if "price" not in clean:
                result.errors.append(f"«{title}»: нет цены, пропущено.")
                continue
            clean.setdefault("description", "")

            product = Product(**clean)
            try:
                pk = int(pk) if pk not in (None, "") else None
            except (TypeError, ValueError):
                pk = None
            if pk and not Product.objects.filter(pk=pk).exists():
                product.pk = pk
            product.save_base(raw=True, force_insert=True)
            existing_by_title[title.lower()] = product
            result.created += 1

        if result.created:
            _reset_sequence()

    return result

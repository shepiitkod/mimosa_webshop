"""Vercel build step: apply database migrations on production deployments.

Vercel runs collectstatic itself. Migrations run only for production builds,
against the direct (unpooled) database connection, so preview builds never
touch the live schema.

One-time Render -> Neon copy: when RENDER_DATABASE_URL is set and the target
database has no products yet, the data is dumped from Render and loaded into
the new database. Remove RENDER_DATABASE_URL once the copy is done.
"""

import os
import subprocess
import sys

DUMP_FILE = "/tmp/render_dump.json"
DUMP_EXCLUDE = [
    "contenttypes",
    "auth.permission",
    "admin.logentry",
    "sessions",
]


def manage(*args: str, database_url: str) -> int:
    env = dict(os.environ, DATABASE_URL=database_url)
    return subprocess.call([sys.executable, "manage.py", *args], env=env)


def target_has_products(database_url: str) -> bool:
    code = (
        "from django.db import connection\n"
        "from shop.models import Product\n"
        "has = 'shop_product' in connection.introspection.table_names() "
        "and Product.objects.exists()\n"
        "raise SystemExit(10 if has else 0)\n"
    )
    return manage("shell", "-c", code, database_url=database_url) == 10


def copy_from_render(source_url: str, target_url: str) -> int:
    if target_has_products(target_url):
        print("[vercel_build] Target already has products: skipping Render copy")
        return 0

    print("[vercel_build] Dumping data from Render")
    excludes = [arg for app in DUMP_EXCLUDE for arg in ("-e", app)]
    rc = manage(
        "dumpdata",
        "--natural-foreign",
        "--natural-primary",
        *excludes,
        "-o",
        DUMP_FILE,
        database_url=source_url,
    )
    if rc != 0:
        print("[vercel_build] dumpdata failed")
        return rc
    print(f"[vercel_build] Dump size: {os.path.getsize(DUMP_FILE)} bytes")

    rc = manage("migrate", "--noinput", database_url=target_url)
    if rc != 0:
        return rc

    print("[vercel_build] Loading data into the new database")
    rc = manage("loaddata", DUMP_FILE, database_url=target_url)
    if rc != 0:
        print("[vercel_build] loaddata failed")
        return rc

    # Primary-key sequences must continue after the copied rows.
    code = (
        "from django.core.management import call_command\n"
        "from django.db import connection\n"
        "from io import StringIO\n"
        "out = StringIO()\n"
        "for app in ('auth', 'shop'):\n"
        "    call_command('sqlsequencereset', app, stdout=out)\n"
        "if connection.vendor == 'postgresql' and out.getvalue().strip():\n"
        "    with connection.cursor() as c:\n"
        "        c.execute(out.getvalue())\n"
        "from shop.models import Product, Order\n"
        "from django.contrib.auth.models import User\n"
        "print('[vercel_build] Copied: products=%d orders=%d users=%d' % "
        "(Product.objects.count(), Order.objects.count(), User.objects.count()))\n"
    )
    return manage("shell", "-c", code, database_url=target_url)


def main() -> int:
    env = os.environ.get("VERCEL_ENV", "")
    if env != "production":
        print(f"[vercel_build] VERCEL_ENV={env or 'unset'}: skipping migrations")
        return 0

    target_url = os.environ.get("DATABASE_URL_UNPOOLED") or os.environ.get(
        "DATABASE_URL", ""
    )
    if not target_url:
        print("[vercel_build] No DATABASE_URL: skipping migrations")
        return 0

    source_url = os.environ.get("RENDER_DATABASE_URL")
    if source_url:
        rc = copy_from_render(source_url, target_url)
        if rc != 0:
            return rc

    print("[vercel_build] Running migrations")
    return manage("migrate", "--noinput", database_url=target_url)


if __name__ == "__main__":
    sys.exit(main())

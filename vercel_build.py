"""Vercel build step for production deployments.

Vercel runs collectstatic itself. On production builds this script:

1. applies database migrations against the direct (unpooled) connection;
2. creates the first admin account if DJANGO_SUPERUSER_USERNAME,
   DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD are set and that
   user doesn't exist yet. Remove DJANGO_SUPERUSER_PASSWORD from the project
   settings once you've logged in.

Preview builds never touch the database.
"""

import os
import subprocess
import sys


def manage(*args: str, database_url: str) -> int:
    env = dict(os.environ, DATABASE_URL=database_url)
    return subprocess.call([sys.executable, "manage.py", *args], env=env)


def ensure_superuser(database_url: str) -> int:
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    if not (
        username
        and os.environ.get("DJANGO_SUPERUSER_EMAIL")
        and os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    ):
        return 0

    code = (
        "import os\n"
        "from django.contrib.auth import get_user_model\n"
        "exists = get_user_model().objects.filter("
        "username=os.environ['DJANGO_SUPERUSER_USERNAME']).exists()\n"
        "raise SystemExit(10 if exists else 0)\n"
    )
    if manage("shell", "-c", code, database_url=database_url) == 10:
        print(f"[vercel_build] Admin '{username}' already exists: skipping")
        return 0

    print(f"[vercel_build] Creating admin '{username}'")
    return manage("createsuperuser", "--noinput", database_url=database_url)


def main() -> int:
    env = os.environ.get("VERCEL_ENV", "")
    if env != "production":
        print(f"[vercel_build] VERCEL_ENV={env or 'unset'}: skipping migrations")
        return 0

    database_url = os.environ.get("DATABASE_URL_UNPOOLED") or os.environ.get(
        "DATABASE_URL", ""
    )
    if not database_url:
        print("[vercel_build] No DATABASE_URL: skipping migrations")
        return 0

    print("[vercel_build] Running migrations")
    rc = manage("migrate", "--noinput", database_url=database_url)
    if rc != 0:
        return rc

    return ensure_superuser(database_url)


if __name__ == "__main__":
    sys.exit(main())

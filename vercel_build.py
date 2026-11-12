"""Vercel build step: apply database migrations on production deployments.

Vercel runs collectstatic itself. Migrations run only for production builds,
against the direct (unpooled) database connection, so preview builds never
touch the live schema.
"""

import os
import subprocess
import sys


def main() -> int:
    env = os.environ.get("VERCEL_ENV", "")
    if env != "production":
        print(f"[vercel_build] VERCEL_ENV={env or 'unset'}: skipping migrations")
        return 0

    run_env = dict(os.environ)
    direct_url = os.environ.get("DATABASE_URL_UNPOOLED")
    if direct_url:
        run_env["DATABASE_URL"] = direct_url

    print("[vercel_build] Running migrations")
    return subprocess.call(
        [sys.executable, "manage.py", "migrate", "--noinput"], env=run_env
    )


if __name__ == "__main__":
    sys.exit(main())

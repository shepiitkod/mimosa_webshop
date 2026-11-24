"""Create the site owner's admin account on a fresh database.

Only the password hash is stored here (the repository is public). The account
is created once; if it already exists it is left untouched, so a password
changed later in the admin is never overwritten.
"""

from django.db import migrations

OWNER_USERNAME = "shepiitkod"
OWNER_PASSWORD_HASH = (
    "pbkdf2_sha256$1200000$u9pnh8PbvMWOuIB7bdJqKq$"
    "d2YQys+lhnPFxJiOGNdoiTpVw1DAv5xfXDDceqkgMs4="
)


def create_owner(apps, schema_editor):
    User = apps.get_model("auth", "User")
    if User.objects.filter(username=OWNER_USERNAME).exists():
        return
    User.objects.create(
        username=OWNER_USERNAME,
        password=OWNER_PASSWORD_HASH,
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("shop", "0020_alter_product_category"),
    ]

    operations = [migrations.RunPython(create_owner, migrations.RunPython.noop)]

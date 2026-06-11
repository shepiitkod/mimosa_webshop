from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0016_order_tracking_status_notes"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContestEntry",
            fields=[],
            options={
                "verbose_name": "Contest entry",
                "verbose_name_plural": "Contest entries",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("shop.order",),
        ),
    ]

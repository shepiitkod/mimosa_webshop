from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0018_orderitem_selected_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="i18n",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]

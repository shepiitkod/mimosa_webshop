from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0017_contestentry_proxy"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="selected_color_name",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="selected_color_hex",
            field=models.CharField(blank=True, default="", max_length=16),
        ),
    ]

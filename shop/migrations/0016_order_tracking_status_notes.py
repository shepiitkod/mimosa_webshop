import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0015_product_image_focal_points"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="tracking_number",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="order",
            name="tracking_url",
            field=models.URLField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="order",
            name="admin_note",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="status_updated_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

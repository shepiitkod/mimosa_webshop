from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0008_rename_decorative_rose_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="hs_code",
            field=models.CharField(blank=True, default="340600", max_length=20, null=True),
        ),
    ]

from django.db import migrations, models


OLD_CATEGORY_VALUES = [
    "Decorative Rose",
    "Декоративная роза",
    "Rose décorative",
    "Декоративна троянда",
]
NEW_CATEGORY_VALUE = "Decorative Candles"


def rename_category_forward(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    Product.objects.filter(category__in=OLD_CATEGORY_VALUES).update(
        category=NEW_CATEGORY_VALUE
    )


def rename_category_backward(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    Product.objects.filter(category=NEW_CATEGORY_VALUE).update(
        category="Decorative Rose"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0007_rename_address_to_shipping_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.CharField(
                choices=[
                    ("Bento Candles", "Bento Candles"),
                    ("Scented Candles", "Scented Candles"),
                    ("Decorative Candles", "Decorative Candles"),
                    ("Gift Collections", "Gift Collections"),
                    ("New Arrivals", "New Arrivals"),
                ],
                default="New Arrivals",
                max_length=120,
            ),
        ),
        migrations.RunPython(rename_category_forward, rename_category_backward),
    ]

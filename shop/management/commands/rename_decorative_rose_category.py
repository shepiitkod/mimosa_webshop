from django.core.management.base import BaseCommand

from shop.models import Product


OLD_CATEGORY_VALUES = [
    "Decorative Rose",
    "Декоративная роза",
    "Rose décorative",
    "Декоративна троянда",
]
NEW_CATEGORY_VALUE = "Decorative Candles"


class Command(BaseCommand):
    help = "Rename old Decorative Rose category values to Decorative Candles."

    def handle(self, *args, **options):
        updated = Product.objects.filter(category__in=OLD_CATEGORY_VALUES).update(
            category=NEW_CATEGORY_VALUE
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} product(s) to category '{NEW_CATEGORY_VALUE}'."
            )
        )

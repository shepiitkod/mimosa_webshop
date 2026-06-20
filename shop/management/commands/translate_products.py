import json

from django.core.management.base import BaseCommand

from shop.models import Product
from shop.translation_service import sync_product_translations


class Command(BaseCommand):
    help = "Generate or refresh storefront translations for all products."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-translate every product even if source text did not change.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        updated = 0

        for product in Product.objects.order_by("id"):
            if sync_product_translations(product, force=force):
                updated += 1
                self.stdout.write(f"Translated product #{product.id}: {product.title}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Updated translations for {updated} product(s)."
            )
        )

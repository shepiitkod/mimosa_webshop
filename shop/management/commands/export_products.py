from django.core.management.base import BaseCommand

from shop.product_transfer import export_products_csv, export_products_json


class Command(BaseCommand):
    help = "Export all products as JSON (default) or CSV to stdout or a file."

    def add_arguments(self, parser):
        parser.add_argument("--format", choices=("json", "csv"), default="json")
        parser.add_argument("-o", "--output")

    def handle(self, *args, **options):
        body = (
            export_products_csv()
            if options["format"] == "csv"
            else export_products_json()
        )
        if options["output"]:
            with open(options["output"], "w", encoding="utf-8") as fh:
                fh.write(body)
        else:
            self.stdout.write(body)

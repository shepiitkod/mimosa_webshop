from django.core.management.base import BaseCommand, CommandError

from shop.product_transfer import import_products


class Command(BaseCommand):
    help = "Import products from a JSON (dumpdata or export) or CSV file."

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Leave products with the same title unchanged.",
        )

    def handle(self, *args, **options):
        try:
            with open(options["path"], encoding="utf-8-sig") as fh:
                text = fh.read()
        except OSError as exc:
            raise CommandError(str(exc)) from exc

        result = import_products(text, update_existing=not options["skip_existing"])
        for error in result.errors:
            self.stderr.write(error)
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {result.created}, updated {result.updated}, "
                f"skipped {result.skipped}."
            )
        )

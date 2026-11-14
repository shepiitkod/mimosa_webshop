"""Demo data for design-review previews (settings.DEMO_PREVIEW only).

Creates the SQLite schema in /tmp and a handful of products whose photos
are the atelier pictures shipped in static/. Never runs in production.
"""

import logging
import os
import threading
from decimal import Decimal

logger = logging.getLogger(__name__)
_lock = threading.Lock()
_done = False

DEMO_PRODUCTS = (
    ("Bougie Pivoine", "Scented Candles", "MAIN9", "MAIN11", "Pivoine & musc blanc", "Coton", "45 h", "34.00"),
    ("Trio Fleurs de Printemps", "Scented Candles", "MAIN11", "MAIN10", "Fleur de cerisier", "Coton", "3 × 20 h", "48.00"),
    ("Bento Étoiles Pastel", "Bento Candles", "MAIN2", "photo3", "", "", "", "29.00"),
    ("Bento Cœurs Dorés", "Bento Candles", "MAIN4", "MAIN5", "", "", "", "32.00"),
    ("Chiffres Roses", "Ceremony Candles", "MAIN6", "MAIN1", "", "", "", "18.00"),
    ("Chiffres Mimosa", "Ceremony Candles", "MAIN7", "MAIN6", "", "", "", "18.00"),
    ("Sphères Florales", "Decorative Candles", "MAIN8", "MAIN12", "", "", "", "26.00"),
    ("Bougies Chauffe-plat Rose", "Decorative Candles", "MAIN12", "MAIN8", "Rose ancienne", "Coton", "6 h", "22.00"),
    ("Sachet Cœur Fleuri", "Plaster Sachets", "sachets-flatlay", "sachets-dressing", "Mimosa", "", "", "14.00"),
    ("Coffret Ailes d’Ange", "Plaster Sachets", "sachets-hero", "sachets-flatlay", "Lavande", "", "", "24.00"),
)


def ensure_demo_database():
    global _done
    if _done:
        return
    with _lock:
        if _done:
            return
        from django.conf import settings
        from django.core.management import call_command

        if not getattr(settings, "DEMO_PREVIEW", False):
            _done = True
            return
        fresh = not os.path.exists(settings.DATABASES["default"]["NAME"])
        call_command("migrate", interactive=False, verbosity=0)
        from .models import Product

        if fresh or not Product.objects.exists():
            for title, cat, a, b, scent, wick, burn, price in DEMO_PRODUCTS:
                Product.objects.create(
                    title=title,
                    category=cat,
                    price=Decimal(price),
                    stock=10,
                    description=(
                        "Coulée à la main dans notre atelier de Nîmes, cire de soja "
                        "naturelle et parfum de Provence. Pièce de démonstration."
                    ),
                    scent=scent,
                    wick=wick,
                    burn_time=burn,
                    image=f"images/{a}.jpg",
                    image_2=f"images/{b}.jpg",
                )
            logger.info("Demo preview database ready.")
        _done = True

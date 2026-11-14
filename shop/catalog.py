"""Shop structure: collections (one per product category) and occasions.

Collections map 1:1 to Product.category. Occasions cut across categories:
a product belongs to an occasion when the staff ticked it in the admin, or,
if nothing was ticked, when its category is in the occasion's defaults.
"""

from django.db.models import Q

from .models import Product

# slug -> collection. Order = order in menus and filters.
COLLECTIONS = (
    {
        "slug": "bento-candles",
        "categories": (Product.CATEGORY_BENTO,),
        "name": "Bento Candles",
        "key": "nav-sub-bento",
        "intro_key": "col-bento-intro",
        "intro": "Petits gâteaux de cire, étoiles et cœurs pastel : la bougie qui fait briller vos célébrations.",
        "image": "assets/images/MAIN2",
        "tint": "bento",
    },
    {
        "slug": "scented-candles",
        "categories": (Product.CATEGORY_SCENTED,),
        "name": "Scented Candles",
        "key": "nav-sub-scented",
        "intro_key": "col-scented-intro",
        "intro": "Cire de soja naturelle et parfums de Provence, coulés en fleurs dans nos coupelles d’atelier.",
        "image": "assets/images/MAIN11",
        "tint": "scented",
    },
    {
        "slug": "decorative-candles",
        "categories": (Product.CATEGORY_DECORATIVE,),
        "name": "Decorative Candles",
        "key": "nav-sub-decorative",
        "intro_key": "col-decorative-intro",
        "intro": "Des sculptures de cire à poser, à offrir, à regarder — et, un soir, à allumer.",
        "image": "assets/images/MAIN8",
        "tint": "decorative",
    },
    {
        "slug": "ceremony-candles",
        "categories": (Product.CATEGORY_CEREMONY, Product.CATEGORY_CEREMONY_LEGACY),
        "name": "Ceremony Candles",
        "key": "nav-sub-ceremony",
        "intro_key": "col-ceremony-intro",
        "intro": "Chiffres, prénoms et bougies de cérémonie, pour les jours que l’on n’oublie pas.",
        "image": "assets/images/MAIN6",
        "tint": "ceremony",
    },
    {
        "slug": "plaster-sachets",
        "categories": (Product.CATEGORY_SACHETS,),
        "name": "Plaster Sachets",
        "key": "nav-sub-sachets",
        "intro_key": "col-sachets-intro",
        "intro": "Sachets parfumés en plâtre, moulés et peints à la main, pour parfumer une armoire, une voiture, une chambre.",
        "image": "assets/images/sachets-hero",
        "tint": "sachets",
    },
    {
        "slug": "gift-collections",
        "categories": (Product.CATEGORY_GIFTS,),
        "name": "Gift Collections",
        "key": "nav-sub-gifts",
        "intro_key": "col-gifts-intro",
        "intro": "Des coffrets composés à l’atelier, prêts à être offerts.",
        "image": "assets/images/MAIN3",
        "tint": "gifts",
    },
)

COLLECTIONS_BY_SLUG = {c["slug"]: c for c in COLLECTIONS}

OCCASIONS = (
    {
        "slug": "anniversaire",
        "name": "Anniversaire",
        "key": "occ-anniversaire",
        "line_key": "occ-anniversaire-line",
        "line": "Chiffres et petits gâteaux de cire",
        "categories": (
            Product.CATEGORY_CEREMONY,
            Product.CATEGORY_CEREMONY_LEGACY,
            Product.CATEGORY_BENTO,
        ),
        "image": "assets/images/MAIN6",
        "w": 801,
        "h": 1200,
    },
    {
        "slug": "mariage-ceremonie",
        "name": "Mariage & Cérémonie",
        "key": "occ-mariage",
        "line_key": "occ-mariage-line",
        "line": "Pour dire oui à la lumière",
        "categories": (
            Product.CATEGORY_CEREMONY,
            Product.CATEGORY_CEREMONY_LEGACY,
            Product.CATEGORY_DECORATIVE,
        ),
        "image": "assets/images/contest-bouquet",
        "w": 683,
        "h": 1024,
    },
    {
        "slug": "cadeau",
        "name": "Cadeau",
        "key": "occ-cadeau",
        "line_key": "occ-cadeau-line",
        "line": "Emballé à l’atelier, noué d’un ruban",
        "categories": (
            Product.CATEGORY_GIFTS,
            Product.CATEGORY_SACHETS,
            Product.CATEGORY_SCENTED,
        ),
        "image": "assets/images/sachets-hero",
        "w": 928,
        "h": 1200,
    },
    {
        "slug": "maison",
        "name": "Pour la maison",
        "key": "occ-maison",
        "line_key": "occ-maison-line",
        "line": "La douceur d’une flamme, chaque soir",
        "categories": (
            Product.CATEGORY_SCENTED,
            Product.CATEGORY_DECORATIVE,
            Product.CATEGORY_SACHETS,
        ),
        "image": "assets/images/MAIN11",
        "w": 801,
        "h": 1200,
    },
)

OCCASIONS_BY_SLUG = {o["slug"]: o for o in OCCASIONS}
OCCASION_CHOICES = [(o["slug"], o["name"]) for o in OCCASIONS]

# Price filter bands (EUR). Upper bound exclusive.
PRICE_BANDS = (
    {"slug": "moins-25", "key": "price-under-25", "label": "Moins de 25 €", "min": None, "max": 25},
    {"slug": "25-50", "key": "price-25-50", "label": "25 – 50 €", "min": 25, "max": 50},
    {"slug": "plus-50", "key": "price-over-50", "label": "Plus de 50 €", "min": 50, "max": None},
)
PRICE_BANDS_BY_SLUG = {b["slug"]: b for b in PRICE_BANDS}


def occasion_filter(slug):
    """Q object selecting the products of one occasion."""
    occasion = OCCASIONS_BY_SLUG.get(slug)
    if not occasion:
        return Q(pk__in=[])
    explicit = Q(occasions__icontains=slug)
    by_category = Q(occasions="") & Q(category__in=occasion["categories"])
    return explicit | by_category


def collection_for_category(category):
    for collection in COLLECTIONS:
        if category in collection["categories"]:
            return collection
    return None

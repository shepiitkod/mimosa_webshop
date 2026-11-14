from django.conf import settings


def cart(request):
    cart_data = request.session.get('cart', {})
    cart_items_count = 0
    for raw_item in cart_data.values():
        if isinstance(raw_item, dict):
            raw_item = raw_item.get('quantity', 0)
        try:
            cart_items_count += int(raw_item)
        except (TypeError, ValueError):
            continue
    return {
        'cart_items_count': cart_items_count,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }


def navigation(request):
    """Collections and occasions for the header mega menu and the footer."""
    from .catalog import COLLECTIONS, OCCASIONS

    return {
        'nav_collections': [c for c in COLLECTIONS if c['slug'] != 'gift-collections'],
        'nav_occasions': OCCASIONS,
    }

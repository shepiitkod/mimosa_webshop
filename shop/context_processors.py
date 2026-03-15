from django.conf import settings


def cart(request):
    cart_data = request.session.get('cart', {})
    cart_items_count = sum(int(qty) for qty in cart_data.values())
    return {
        'cart_items_count': cart_items_count,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }

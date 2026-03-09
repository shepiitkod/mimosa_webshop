def cart(request):
    cart_data = request.session.get('cart', {})
    cart_items_count = sum(int(qty) for qty in cart_data.values())
    return {
        'cart_items_count': cart_items_count,
    }

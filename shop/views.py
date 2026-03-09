from decimal import Decimal, InvalidOperation
import json

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Order, OrderItem, Product


@require_GET
def index_view(request):
	products = Product.objects.all()
	return render(request, 'index.html', {'products': products})


def _to_cents(amount: Decimal) -> int:
	try:
		normalized = Decimal(amount).quantize(Decimal('0.01'))
	except (InvalidOperation, TypeError):
		raise ValueError('Invalid order amount')

	cents = int(normalized * 100)
	if cents <= 0:
		raise ValueError('Order amount must be greater than zero')
	return cents


@csrf_exempt
@login_required
@require_POST
def create_order_from_product(request):
	try:
		payload = json.loads(request.body.decode('utf-8'))
	except (json.JSONDecodeError, UnicodeDecodeError):
		return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

	title = (payload.get('title') or '').strip()
	if not title:
		return JsonResponse({'error': 'Product title is required.'}, status=400)

	quantity = payload.get('quantity', 1)
	try:
		quantity = int(quantity)
	except (TypeError, ValueError):
		return JsonResponse({'error': 'Quantity must be an integer.'}, status=400)
	if quantity <= 0:
		return JsonResponse({'error': 'Quantity must be greater than zero.'}, status=400)

	raw_price = payload.get('price')
	try:
		price = Decimal(str(raw_price)).quantize(Decimal('0.01'))
	except (InvalidOperation, TypeError):
		return JsonResponse({'error': 'Price must be a valid number.'}, status=400)
	if price <= 0:
		return JsonResponse({'error': 'Price must be greater than zero.'}, status=400)

	category = (payload.get('category') or 'General').strip() or 'General'
	description = (payload.get('description') or 'Product from storefront').strip() or 'Product from storefront'

	with transaction.atomic():
		product, _ = Product.objects.get_or_create(
			title=title,
			defaults={
				'description': description,
				'price': price,
				'category': category,
				'stock': 0,
				'image': payload.get('image') or 'products/placeholder.jpg',
			},
		)

		if product.stock > 0 and quantity > product.stock:
			return JsonResponse({'error': 'Not enough stock available.'}, status=400)

		price_at_purchase = product.price
		total_amount = (price_at_purchase * quantity).quantize(Decimal('0.01'))
		order = Order.objects.create(
			user=request.user,
			total_amount=total_amount,
			status=Order.STATUS_PROCESSING,
		)
		OrderItem.objects.create(
			order=order,
			product=product,
			quantity=quantity,
			price_at_purchase=price_at_purchase,
		)

		if product.stock > 0:
			product.stock -= quantity
			product.save(update_fields=['stock'])

	return JsonResponse(
		{
			'status': 'ok',
			'order_id': order.id,
			'product': product.title,
			'quantity': quantity,
			'total_amount': str(order.total_amount),
		},
		status=201,
	)


@login_required
@require_POST
def create_checkout_session(request, order_id):
	if not settings.STRIPE_SECRET_KEY:
		return HttpResponse('Stripe secret key is not configured.', status=500)

	stripe.api_key = settings.STRIPE_SECRET_KEY
	order = get_object_or_404(Order, id=order_id, user=request.user)

	if order.status == Order.STATUS_PAID:
		return redirect('shop:payment_success')

	try:
		unit_amount = _to_cents(order.total_amount)
	except ValueError as exc:
		return HttpResponse(str(exc), status=400)

	root_url = request.build_absolute_uri('/')
	success_url = f"{root_url}payments/success/?session_id={{CHECKOUT_SESSION_ID}}"
	cancel_url = f"{root_url}payments/cancel/"

	checkout_session = stripe.checkout.Session.create(
		mode='payment',
		line_items=[
			{
				'price_data': {
					'currency': 'eur',
					'product_data': {
						'name': f'Order #{order.id}',
						'description': f'Order contains {order.items.count()} item(s)',
					},
					'unit_amount': unit_amount,
				},
				'quantity': 1,
			}
		],
		metadata={'order_id': str(order.id)},
		client_reference_id=str(order.id),
		customer_email=order.user.email or None,
		success_url=success_url,
		cancel_url=cancel_url,
	)

	return redirect(checkout_session.url, permanent=False)


@require_GET
def payment_success(request):
	return HttpResponse('Payment successful. Thank you for your order!')


@require_GET
def payment_cancel(request):
	return HttpResponse('Payment canceled. You can try again anytime.')


@csrf_exempt
@require_POST
def stripe_webhook(request):
	if not settings.STRIPE_SECRET_KEY:
		return JsonResponse({'error': 'Stripe secret key is not configured.'}, status=500)
	if not settings.STRIPE_WEBHOOK_SECRET:
		return JsonResponse({'error': 'Stripe webhook secret is not configured.'}, status=500)

	stripe.api_key = settings.STRIPE_SECRET_KEY
	payload = request.body
	sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

	try:
		event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
	except (ValueError, stripe.error.SignatureVerificationError):
		return JsonResponse({'error': 'Invalid webhook payload.'}, status=400)

	if event['type'] == 'checkout.session.completed':
		session_data = event['data']['object']
		metadata = session_data.get('metadata', {})
		order_id = metadata.get('order_id') or session_data.get('client_reference_id')

		if order_id:
			try:
				order = Order.objects.get(id=order_id)
				order.status = Order.STATUS_PAID
				order.save(update_fields=['status'])
			except Order.DoesNotExist:
				return JsonResponse({'error': 'Order not found.'}, status=404)

	return JsonResponse({'status': 'ok'})

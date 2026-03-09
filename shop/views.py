from decimal import Decimal, InvalidOperation
import json

import stripe
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Order, OrderItem, Product


def _to_cents(amount: Decimal) -> int:
	try:
		normalized = Decimal(amount).quantize(Decimal('0.01'))
	except (InvalidOperation, TypeError):
		raise ValueError('Invalid order amount')

	cents = int(normalized * 100)
	if cents <= 0:
		raise ValueError('Order amount must be greater than zero')
	return cents


def _create_stripe_session_for_order(request, order):
	if not settings.STRIPE_SECRET_KEY:
		raise ValueError('Stripe secret key is not configured.')

	stripe.api_key = settings.STRIPE_SECRET_KEY
	unit_amount = _to_cents(order.total_amount)

	root_url = request.build_absolute_uri('/')
	success_url = f"{root_url}payments/success/?session_id={{CHECKOUT_SESSION_ID}}"
	cancel_url = f"{root_url}payments/cancel/"

	return stripe.checkout.Session.create(
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


def _get_cart(session):
	return session.setdefault('cart', {})


def _cart_summary(session):
	cart = _get_cart(session)
	if not cart:
		return [], Decimal('0.00')

	product_ids = [int(pid) for pid in cart.keys()]
	products = Product.objects.filter(id__in=product_ids)
	products_map = {product.id: product for product in products}

	items = []
	total = Decimal('0.00')

	for pid_str, quantity in cart.items():
		product = products_map.get(int(pid_str))
		if not product:
			continue
		qty = int(quantity)
		line_total = (product.price * qty).quantize(Decimal('0.01'))
		total += line_total
		items.append(
			{
				'product': product,
				'quantity': qty,
				'line_total': line_total,
			}
		)

	return items, total.quantize(Decimal('0.01'))


@require_GET
def index_view(request):
	products = Product.objects.all()
	cart_count = sum(int(qty) for qty in _get_cart(request.session).values())
	return render(request, 'index.html', {'products': products, 'cart_count': cart_count})


@require_GET
def about_view(request):
	return render(request, 'About.html')


@require_GET
def contact_view(request):
	return render(request, 'contact.html')


@require_GET
def confidential_view(request):
	return render(request, 'confidential.html')


@require_GET
def product_bento_view(request):
	return render(request, 'products1.html')


@require_GET
def product_rose_view(request):
	return render(request, 'products3.html')


@require_GET
def login_view(request):
	form = AuthenticationForm()
	return render(request, 'registration/login.html', {'form': form})


@require_POST
def login_submit(request):
	form = AuthenticationForm(request, data=request.POST)
	if form.is_valid():
		login(request, form.get_user())
		return redirect('shop:profile')
	return render(request, 'registration/login.html', {'form': form})


@require_GET
def register_view(request):
	form = UserCreationForm()
	return render(request, 'registration/register.html', {'form': form})


@require_POST
def register_submit(request):
	form = UserCreationForm(request.POST)
	if form.is_valid():
		user = form.save()
		login(request, user)
		return redirect('shop:profile')
	return render(request, 'registration/register.html', {'form': form})


@require_GET
def logout_view(request):
	logout(request)
	return redirect('shop:home')


@login_required
@require_GET
def profile_view(request):
	orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
	return render(request, 'profile.html', {'orders': orders})


@require_POST
def cart_add(request, product_id):
	get_object_or_404(Product, id=product_id)
	quantity = int(request.POST.get('quantity', 1) or 1)
	update = request.POST.get('update') == '1'

	if quantity < 1:
		quantity = 1

	cart = _get_cart(request.session)
	pid = str(product_id)

	if update:
		cart[pid] = quantity
	else:
		cart[pid] = int(cart.get(pid, 0)) + quantity

	request.session.modified = True
	return redirect('shop:cart_detail')


@require_GET
def cart_detail(request):
	items, total = _cart_summary(request.session)
	return render(request, 'cart.html', {'cart_items': items, 'cart_total': total})


@require_POST
def cart_remove(request, product_id):
	cart = _get_cart(request.session)
	pid = str(product_id)
	if pid in cart:
		del cart[pid]
		request.session.modified = True
	return redirect('shop:cart_detail')


@login_required
@require_POST
def order_create(request):
	items, total = _cart_summary(request.session)
	if not items:
		return redirect('shop:cart_detail')

	with transaction.atomic():
		order = Order.objects.create(
			user=request.user,
			total_amount=total,
			status=Order.STATUS_PROCESSING,
		)

		for item in items:
			OrderItem.objects.create(
				order=order,
				product=item['product'],
				quantity=item['quantity'],
				price_at_purchase=item['product'].price,
			)

	request.session['cart'] = {}
	request.session.modified = True

	try:
		session = _create_stripe_session_for_order(request, order)
	except ValueError as exc:
		return HttpResponse(str(exc), status=500)

	return redirect(session.url, permanent=False)


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

		price_at_purchase = product.price
		total_amount = (price_at_purchase * quantity).quantize(Decimal('0.01'))
		order = Order.objects.create(user=request.user, total_amount=total_amount, status=Order.STATUS_PROCESSING)
		OrderItem.objects.create(order=order, product=product, quantity=quantity, price_at_purchase=price_at_purchase)

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
	order = get_object_or_404(Order, id=order_id, user=request.user)

	if order.status == Order.STATUS_PAID:
		return redirect('shop:payment_success')

	try:
		session = _create_stripe_session_for_order(request, order)
	except ValueError as exc:
		return HttpResponse(str(exc), status=500)

	return redirect(session.url, permanent=False)


@require_GET
def payment_success(request):
	return render(request, 'payment_success.html')


@require_GET
def payment_cancel(request):
	return render(request, 'payment_cancel.html')


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

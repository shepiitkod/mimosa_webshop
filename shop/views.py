from decimal import Decimal, InvalidOperation
import json
import traceback
from typing import Optional

import stripe
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Count, Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import NewsletterUser, Order, OrderItem, Product


CATEGORY_SLUG_ALIASES = {
	'decorative-rose': 'decorative-candles',
}


def _to_cents(amount: Decimal) -> int:
	try:
		normalized = Decimal(amount).quantize(Decimal('0.01'))
	except (InvalidOperation, TypeError):
		raise ValueError('Invalid order amount')

	cents = int(normalized * 100)
	if cents <= 0:
		raise ValueError('Order amount must be greater than zero')
	return cents


def _build_site_url(path: str) -> str:
	base_url = (settings.SITE_URL or '').rstrip('/')
	if not base_url:
		raise ValueError('Site URL is not configured.')
	return f'{base_url}{path}'


def _create_stripe_session_for_order(request, order):
	if not settings.STRIPE_SECRET_KEY:
		raise ValueError('Stripe secret key is not configured.')

	stripe.api_key = settings.STRIPE_SECRET_KEY
	order_items = list(order.items.select_related('product').all())
	unit_amount = _to_cents(order.total_amount)
	hs_codes = sorted(
		{
			(item.product.hs_code or '340600')
			for item in order_items
		}
	)

	success_url = f"{_build_site_url(reverse('shop:success'))}?session_id={{CHECKOUT_SESSION_ID}}"
	cancel_url = _build_site_url(reverse('shop:cart'))

	return stripe.checkout.Session.create(
		payment_method_types=['card'],
		client_reference_id=str(order.id),
		metadata={
			'order_id': str(order.id),
			'hs_codes': ','.join(hs_codes),
			'primary_hs_code': hs_codes[0] if hs_codes else '340600',
		},
		line_items=[
			{
				'price_data': {
					'currency': 'eur',
					'product_data': {
						'name': f'Order #{order.id}',
						'description': f'Order contains {len(order_items)} item(s)',
					},
					'unit_amount': unit_amount,
				},
				'quantity': 1,
			}
		],
		mode='payment',
		allow_promotion_codes=True,
		shipping_address_collection={'allowed_countries': ['FR', 'UA', 'GB', 'US']},
		success_url=success_url,
		cancel_url=cancel_url,
	)


def _amount_total_to_decimal(session_data) -> Optional[Decimal]:
	"""Return Stripe amount_total in Decimal major units (e.g., EUR), if available."""
	if not session_data or not hasattr(session_data, 'get'):
		return None

	amount_total = session_data.get('amount_total')
	if amount_total is None:
		return None

	try:
		return (Decimal(str(amount_total)) / Decimal('100')).quantize(Decimal('0.01'))
	except (InvalidOperation, TypeError, ValueError):
		return None


def _mark_order_paid_from_checkout_session(session_id: str) -> bool:
	if not session_id or not settings.STRIPE_SECRET_KEY:
		return False

	stripe.api_key = settings.STRIPE_SECRET_KEY

	try:
		session_data = stripe.checkout.Session.retrieve(session_id)
	except Exception:
		return False

	metadata = session_data.get('metadata', {}) if hasattr(session_data, 'get') else {}
	order_id = metadata.get('order_id') if metadata else None
	if not order_id and hasattr(session_data, 'get'):
		order_id = session_data.get('client_reference_id')

	if not order_id:
		return False

	try:
		order = Order.objects.get(id=order_id)
	except (Order.DoesNotExist, ValueError, TypeError):
		return False

	updated_fields = []

	# Persist final Stripe amount (after promo codes/discounts) to the order.
	final_amount = _amount_total_to_decimal(session_data)
	if final_amount is not None and order.total_amount != final_amount:
		order.total_amount = final_amount
		updated_fields.append('total_amount')

	# Persist shipping details coming from Stripe Checkout.
	shipping_details = session_data.get('shipping_details')
	if shipping_details and shipping_details.get('address'):
		address_data = shipping_details.get('address')
		order.shipping_address = address_data.get('line1', '')
		order.city = address_data.get('city', '')
		order.postal_code = address_data.get('postal_code', '')
		order.country = address_data.get('country', '')
		updated_fields.extend(['shipping_address', 'city', 'postal_code', 'country'])

	if order.status != Order.STATUS_PAID:
		order.status = Order.STATUS_PAID
		updated_fields.append('status')

	if updated_fields:
		order.save(update_fields=sorted(set(updated_fields)))

	return True


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
def products_catalog_view(request, category_slug=None):
	if category_slug in CATEGORY_SLUG_ALIASES:
		return redirect(
			'shop:products_by_category',
			category_slug=CATEGORY_SLUG_ALIASES[category_slug],
			permanent=True,
		)

	products_qs = Product.objects.all().order_by('title')
	counts_map = {
		row['category']: row['total']
		for row in Product.objects.values('category').annotate(total=Count('id'))
	}

	category_items = []
	for name, _label in Product.CATEGORY_CHOICES:
		category_items.append(
			{
				'name': name,
				'slug': slugify(name),
				'count': counts_map.get(name, 0),
			}
		)

	active_category = None
	if category_slug:
		active_category = next((item for item in category_items if item['slug'] == category_slug), None)
		if active_category:
			products_qs = products_qs.filter(category=active_category['name'])

	total_products_count = Product.objects.count()

	cart_count = sum(int(qty) for qty in _get_cart(request.session).values())
	return render(
		request,
		'products_catalog.html',
		{
			'products': products_qs,
			'total_products_count': total_products_count,
			'categories': category_items,
			'active_category': active_category,
			'cart_count': cart_count,
		},
	)


@require_GET
def product_detail_view(request, product_id, slug=None):
	product = get_object_or_404(Product, id=product_id)
	canonical_slug = slugify(product.title)
	if slug != canonical_slug:
		return redirect('shop:product_detail', product_id=product.id, slug=canonical_slug)

	related_products = (
		Product.objects.filter(category=product.category)
		.exclude(id=product.id)
		.order_by('title')[:4]
	)

	return render(
		request,
		'product_detail.html',
		{
			'product': product,
			'canonical_slug': canonical_slug,
			'related_products': related_products,
		},
	)


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
	orders = (
		Order.objects.filter(user=request.user)
		.prefetch_related(
			Prefetch('items', queryset=OrderItem.objects.select_related('product'))
		)
		.order_by('-created_at')
	)
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
	except Exception as e:
		print(str(e))
		return HttpResponse(str(e), status=500)

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

	category = (payload.get('category') or Product.CATEGORY_NEW).strip() or Product.CATEGORY_NEW
	allowed_categories = {value for value, _label in Product.CATEGORY_CHOICES}
	if category not in allowed_categories:
		category = Product.CATEGORY_NEW
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
def create_checkout_session(request):
	try:
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

		session = _create_stripe_session_for_order(request, order)
		return redirect(session.url, permanent=False)
	except Exception as e:
		error_message = traceback.format_exc()
		print(error_message)
		return HttpResponse(f'<pre>{error_message}</pre>', status=200)


@login_required
@require_POST
def create_checkout_session_for_order(request, order_id):
	order = get_object_or_404(Order, id=order_id, user=request.user)

	if order.status == Order.STATUS_PAID:
		return redirect('shop:payment_success')

	try:
		session = _create_stripe_session_for_order(request, order)
	except Exception as e:
		print(str(e))
		return HttpResponse(str(e), status=500)

	return redirect(session.url, permanent=False)


@require_GET
def payment_success(request):
	return render(request, 'payment_success.html')


@require_GET
def payment_cancel(request):
	return render(request, 'payment_cancel.html')


@require_GET
def checkout_success(request):
	session_id = request.GET.get('session_id', '')
	payment_verified = _mark_order_paid_from_checkout_session(session_id)
	return render(request, 'success.html', {'payment_verified': payment_verified})


@require_GET
def checkout_cancel(request):
	return render(request, 'cancel.html')


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
		payment_status = session_data.get('payment_status')
		if payment_status and payment_status != 'paid':
			return JsonResponse({'status': 'ignored', 'reason': 'payment not completed'})

		metadata = session_data.get('metadata', {})
		order_id = metadata.get('order_id') or session_data.get('client_reference_id')

		if order_id:
			try:
				order = Order.objects.get(id=order_id)

				final_amount = _amount_total_to_decimal(session_data)
				updated_fields = []
				if final_amount is not None and order.total_amount != final_amount:
					order.total_amount = final_amount
					updated_fields.append('total_amount')

				order.status = Order.STATUS_PAID
				updated_fields.append('status')

				shipping_details = session_data.get('shipping_details') or {}
				address_data = shipping_details.get('address') or {}
				if address_data:
					try:
						order.shipping_address = address_data.get('line1', '')
						order.city = address_data.get('city', '')
						order.postal_code = address_data.get('postal_code', '')
						order.country = address_data.get('country', '')
						updated_fields.extend(['shipping_address', 'city', 'postal_code', 'country'])
					except Exception as e:
						print(f'Webhook shipping save failed for order {order.id}: {e}')

				if updated_fields:
					order.save(update_fields=sorted(set(updated_fields)))
			except Order.DoesNotExist:
				return JsonResponse({'error': 'Order not found.'}, status=404)

	return JsonResponse({'status': 'ok'})


@require_POST
def subscribe_newsletter(request):
	"""Handle newsletter subscription via AJAX."""
	try:
		data = json.loads(request.body)
		email = data.get('email', '').strip().lower()

		if not email:
			return JsonResponse({'success': False, 'error': 'Email is required.'}, status=400)

		try:
			validate_email(email)
		except ValidationError:
			return JsonResponse({'success': False, 'error': 'Please enter a valid email address.'}, status=400)

		if NewsletterUser.objects.filter(email__iexact=email).exists():
			return JsonResponse({'success': False, 'error': 'Email already subscribed'}, status=400)

		try:
			NewsletterUser.objects.create(email=email)
		except IntegrityError:
			return JsonResponse({'success': False, 'error': 'Email already subscribed'}, status=400)

		return JsonResponse({
			'success': True,
			'message': 'Thank you for joining our journey!'
		})

	except json.JSONDecodeError:
		return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
	except Exception as exc:
		return JsonResponse({'success': False, 'error': str(exc)}, status=500)

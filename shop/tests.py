import json
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils.text import slugify
from django.urls import reverse

from .models import Order, Product


class ProductImageFramingTests(TestCase):
	def test_product_image_position_properties(self):
		product = Product.objects.create(
			title='Framed Candle',
			description='Test description',
			price=Decimal('22.00'),
			image='products/framed.jpg',
			image_focal_x=25,
			image_focal_y=75,
			image_2='products/framed-2.jpg',
			image_2_focal_x=80,
			image_2_focal_y=20,
			category=Product.CATEGORY_SCENTED,
		)

		self.assertEqual(product.image_object_position, '25% 75%')
		self.assertEqual(product.image_2_object_position, '80% 20%')

	def test_public_pages_use_saved_image_framing(self):
		product = Product.objects.create(
			title='Catalog Candle',
			description='Test description',
			price=Decimal('18.00'),
			image='products/catalog.jpg',
			image_focal_x=30,
			image_focal_y=70,
			category=Product.CATEGORY_SCENTED,
		)

		catalog_response = self.client.get(reverse('shop:products'))
		self.assertContains(catalog_response, '--product-image-position: 30% 70%')

		detail_response = self.client.get(
			reverse('shop:product_detail', args=[product.id, slugify(product.title)])
		)
		self.assertContains(detail_response, 'data-object-position="30% 70%"')


@override_settings(
	STRIPE_SECRET_KEY='sk_test_dummy',
	STRIPE_WEBHOOK_SECRET='whsec_dummy',
	SITE_URL='https://mimosa-atelier.com',
	SECURE_SSL_REDIRECT=False,
	DEBUG=True,
)
class PaymentSyncTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='payer', password='test12345')
		self.product = Product.objects.create(
			title='Test Candle',
			description='Test description',
			price=Decimal('12.50'),
			image='products/test.jpg',
			category=Product.CATEGORY_SCENTED,
		)
		self.order = Order.objects.create(
			user=self.user,
			total_amount=Decimal('12.50'),
			status=Order.STATUS_PROCESSING,
		)

	def test_checkout_create_then_success_marks_order_paid(self):
		self.client.login(username='payer', password='test12345')

		session = self.client.session
		session['cart'] = {str(self.product.id): 1}
		session.save()

		with patch('shop.views.stripe.checkout.Session.create') as create_mock:
			create_mock.return_value = SimpleNamespace(url='https://checkout.stripe.com/c/pay/cs_test_mock')
			response = self.client.post(
				reverse('shop:create_checkout_session'),
				{'shipping_country': 'FR', 'shipping_carrier': 'colissimo'},
			)
			create_kwargs = create_mock.call_args.kwargs
			self.assertTrue(create_kwargs.get('allow_promotion_codes'))
			self.assertEqual(
				create_kwargs.get('success_url'),
				'https://mimosa-atelier.com/success/?session_id={CHECKOUT_SESSION_ID}',
			)
			self.assertEqual(create_kwargs.get('cancel_url'), 'https://mimosa-atelier.com/cart/')

		self.assertEqual(response.status_code, 302)
		self.assertIn('checkout.stripe.com', response.url)

		created_order = Order.objects.exclude(id=self.order.id).latest('id')
		self.assertEqual(created_order.status, Order.STATUS_PROCESSING)

		with patch('shop.views.stripe.checkout.Session.retrieve') as retrieve_mock:
			retrieve_mock.return_value = {
				'metadata': {'order_id': str(created_order.id)},
				'client_reference_id': str(created_order.id),
				'amount_total': 1000,
			}
			success_response = self.client.get(reverse('shop:success'), {'session_id': 'cs_test_mock'})

		self.assertEqual(success_response.status_code, 200)
		created_order.refresh_from_db()
		self.assertEqual(created_order.status, Order.STATUS_PAID)
		self.assertEqual(created_order.total_amount, Decimal('10.00'))

	def test_checkout_success_marks_order_paid_from_session(self):
		self.client.login(username='payer', password='test12345')

		with patch('shop.views.stripe.checkout.Session.retrieve') as retrieve_mock:
			retrieve_mock.return_value = {
				'metadata': {'order_id': str(self.order.id)},
				'client_reference_id': str(self.order.id),
				'amount_total': 1125,
			}
			response = self.client.get(reverse('shop:success'), {'session_id': 'cs_test_123'})

		self.assertEqual(response.status_code, 200)
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, Order.STATUS_PAID)
		self.assertEqual(self.order.total_amount, Decimal('11.25'))

	def test_stripe_webhook_marks_order_paid(self):
		payload = {
			'type': 'checkout.session.completed',
			'data': {
				'object': {
					'metadata': {'order_id': str(self.order.id)},
					'payment_status': 'paid',
					'amount_total': 900,
				}
			}
		}

		with patch('shop.views.stripe.Webhook.construct_event') as construct_mock:
			construct_mock.return_value = payload
			response = self.client.post(
				reverse('shop:stripe_webhook'),
				data=json.dumps({'ok': True}),
				content_type='application/json',
				HTTP_STRIPE_SIGNATURE='test_signature',
			)

		self.assertEqual(response.status_code, 200)
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, Order.STATUS_PAID)
		self.assertEqual(self.order.total_amount, Decimal('9.00'))

	def test_stripe_webhook_ignores_unpaid_session(self):
		payload = {
			'type': 'checkout.session.completed',
			'data': {
				'object': {
					'metadata': {'order_id': str(self.order.id)},
					'payment_status': 'unpaid',
				}
			}
		}

		with patch('shop.views.stripe.Webhook.construct_event') as construct_mock:
			construct_mock.return_value = payload
			response = self.client.post(
				reverse('shop:stripe_webhook'),
				data=json.dumps({'ok': True}),
				content_type='application/json',
				HTTP_STRIPE_SIGNATURE='test_signature',
			)

		self.assertEqual(response.status_code, 200)
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, Order.STATUS_PROCESSING)


@override_settings(SECURE_SSL_REDIRECT=False)
class CatalogCategoryFilterTests(TestCase):
	def test_plaster_sachets_listed_in_catalog_filter(self):
		Product.objects.create(
			title='Sachet Rose',
			description='Plaster sachet',
			price=Decimal('12.00'),
			image='products/sachet.jpg',
			category=Product.CATEGORY_SACHETS,
		)
		response = self.client.get(reverse('shop:products'))
		self.assertContains(response, 'nav-sub-sachets')
		filtered = self.client.get(
			reverse('shop:products_by_category', args=['plaster-sachets'])
		)
		self.assertContains(filtered, 'Sachet Rose')


import io
import shutil
import tempfile
from datetime import date, timedelta

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import CustomOrderRequest, NewsletterUser, Review


def _png_bytes():
	from PIL import Image

	buf = io.BytesIO()
	Image.new('RGB', (8, 8), (240, 200, 120)).save(buf, format='PNG')
	return buf.getvalue()


def _product(title, category, price='20.00', **extra):
	return Product.objects.create(
		title=title,
		description='Test',
		price=Decimal(price),
		image='products/x.jpg',
		category=category,
		**extra,
	)


@override_settings(SECURE_SSL_REDIRECT=False)
class SiteStructureTests(TestCase):
	def test_old_addresses_redirect_permanently(self):
		cases = {
			'/products/': '/boutique/',
			'/products/category/bento-candles/': '/boutique/bento-candles/',
			'/products/plaster-sachets/': '/boutique/plaster-sachets/',
			'/products/bento/': '/boutique/bento-candles/',
			'/about/': '/atelier/',
		}
		for old, new in cases.items():
			response = self.client.get(old)
			self.assertEqual(response.status_code, 301, old)
			self.assertEqual(response['Location'], new, old)

	def test_legacy_category_redirect_keeps_query(self):
		response = self.client.get('/products/category/bento-candles/?prix=moins-25')
		self.assertEqual(response.status_code, 301)
		self.assertEqual(response['Location'], '/boutique/bento-candles/?prix=moins-25')

	def test_product_pages_keep_their_address(self):
		product = _product('Bougie Test', Product.CATEGORY_SCENTED)
		url = reverse('shop:product_detail', args=[product.id, slugify(product.title)])
		self.assertTrue(url.startswith('/products/'))
		self.assertEqual(self.client.get(url).status_code, 200)

	def test_new_pages_render(self):
		for name in ('shop:home', 'shop:products', 'shop:custom_order', 'shop:atelier', 'shop:faq', 'shop:contact'):
			self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

	def test_unknown_collection_is_404(self):
		self.assertEqual(self.client.get('/boutique/nope/').status_code, 404)

	def test_sitemap_lists_new_pages(self):
		body = self.client.get('/sitemap.xml').content.decode()
		for path in ('/boutique/', '/sur-mesure/', '/atelier/', '/faq/', '/boutique/plaster-sachets/'):
			self.assertIn(path, body)
		self.assertNotIn('/about/', body)


@override_settings(SECURE_SSL_REDIRECT=False)
class BoutiqueFilterTests(TestCase):
	def setUp(self):
		self.numbers = _product('Chiffres', Product.CATEGORY_CEREMONY, '18.00')
		self.scented = _product('Pivoine', Product.CATEGORY_SCENTED, '34.00')
		self.sachet = _product('Sachet', Product.CATEGORY_SACHETS, '60.00')
		self.tagged = _product('Pivoine anniversaire', Product.CATEGORY_SCENTED, '40.00', occasions='anniversaire')

	def titles(self, url):
		return [p.title for p in self.client.get(url).context['products']]

	def test_occasion_follows_category_defaults_and_admin_choice(self):
		titles = self.titles('/boutique/?occasion=anniversaire')
		self.assertIn('Chiffres', titles)
		self.assertIn('Pivoine anniversaire', titles)  # ticked in the admin
		self.assertNotIn('Pivoine', titles)
		self.assertNotIn('Sachet', titles)

	def test_explicit_occasions_override_category(self):
		self.assertNotIn('Pivoine anniversaire', self.titles('/boutique/?occasion=maison'))
		self.assertIn('Pivoine', self.titles('/boutique/?occasion=maison'))

	def test_price_band_and_sort(self):
		self.assertEqual(self.titles('/boutique/?prix=moins-25'), ['Chiffres'])
		self.assertEqual(self.titles('/boutique/?prix=plus-50'), ['Sachet'])
		self.assertEqual(
			self.titles('/boutique/?tri=prix-asc'),
			['Chiffres', 'Pivoine', 'Pivoine anniversaire', 'Sachet'],
		)

	def test_collection_and_filters_combine(self):
		self.assertEqual(self.titles('/boutique/scented-candles/?prix=25-50&tri=prix-desc'), ['Pivoine anniversaire', 'Pivoine'])

	def test_unknown_filter_values_are_ignored(self):
		self.assertEqual(len(self.titles('/boutique/?occasion=x&prix=y&tri=z')), 4)


@override_settings(SECURE_SSL_REDIRECT=False)
class HomepageTests(TestCase):
	def test_shows_up_to_eight_newest_products(self):
		for i in range(10):
			_product(f'Bougie {i}', Product.CATEGORY_SCENTED)
		response = self.client.get('/')
		self.assertEqual(len(response.context['products']), 8)
		self.assertContains(response, 'Bougie 9')
		self.assertNotContains(response, 'Bougie 1<')

	def test_new_arrivals_hidden_without_products(self):
		self.assertNotContains(self.client.get('/'), 'id="nouveautes"')

	def test_reviews_block_hidden_until_published(self):
		Review.objects.create(author_name='Claire', text='Magnifique', is_published=False)
		self.assertNotContains(self.client.get('/'), 'class="avis"')
		Review.objects.create(author_name='Léa', text='Une merveille', is_published=True)
		response = self.client.get('/')
		self.assertContains(response, 'class="avis"')
		self.assertContains(response, 'Une merveille')
		self.assertNotContains(response, 'Magnifique')

	def test_product_page_shows_its_published_reviews_only(self):
		product = _product('Bougie avis', Product.CATEGORY_SCENTED)
		Review.objects.create(author_name='A', text='Pour ce produit', product=product, is_published=True)
		Review.objects.create(author_name='B', text='Brouillon', product=product, is_published=False)
		response = self.client.get(reverse('shop:product_detail', args=[product.id, slugify(product.title)]))
		self.assertContains(response, 'Pour ce produit')
		self.assertNotContains(response, 'Brouillon')

	def test_product_details_hide_empty_fields(self):
		product = _product('Sans détails', Product.CATEGORY_SCENTED)
		response = self.client.get(reverse('shop:product_detail', args=[product.id, slugify(product.title)]))
		self.assertNotContains(response, 'Not specified')
		self.assertNotContains(response, 'pdp-acc-composition')
		self.assertNotContains(response, 'pdp-acc-burn')


@override_settings(
	SECURE_SSL_REDIRECT=False,
	ADMIN_ORDER_EMAIL='owner@example.com',
	EMAIL_HOST_PASSWORD='test',
	EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class CustomOrderTests(TestCase):
	def setUp(self):
		self.media = tempfile.mkdtemp()
		self.override = override_settings(
			MEDIA_ROOT=self.media,
			STORAGES={
				'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
				'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
			},
		)
		self.override.enable()

	def tearDown(self):
		self.override.disable()
		shutil.rmtree(self.media, ignore_errors=True)

	def data(self, **extra):
		payload = {
			'name': 'Camille',
			'email': 'camille@example.com',
			'occasion': 'mariage',
			'event_date': (date.today() + timedelta(days=60)).isoformat(),
			'quantity': '40',
			'message': 'Bougies de table ivoire et or',
			'language': 'fr',
		}
		payload.update(extra)
		return payload

	def test_valid_request_is_saved_and_mailed(self):
		image = SimpleUploadedFile('ref.png', _png_bytes(), content_type='image/png')
		response = self.client.post(reverse('shop:custom_order'), self.data(reference_image=image))
		self.assertEqual(response.status_code, 302)
		self.assertIn('envoye=1', response['Location'])
		obj = CustomOrderRequest.objects.get()
		self.assertEqual(obj.quantity, 40)
		self.assertEqual(obj.language, 'fr')
		self.assertTrue(obj.reference_image.name.startswith('custom_requests/'))
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].to, ['owner@example.com'])
		self.assertEqual(mail.outbox[0].reply_to, ['camille@example.com'])
		self.assertIn('Bougies de table ivoire et or', mail.outbox[0].body)

	def test_thank_you_state(self):
		self.assertContains(self.client.get(reverse('shop:custom_order') + '?envoye=1'), 'sm-sent-title')

	def test_missing_fields_are_rejected(self):
		response = self.client.post(reverse('shop:custom_order'), self.data(message='', email='nope'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'sm-err-required')
		self.assertContains(response, 'sm-err-email')
		self.assertFalse(CustomOrderRequest.objects.exists())
		self.assertEqual(len(mail.outbox), 0)

	def test_past_date_is_rejected(self):
		response = self.client.post(reverse('shop:custom_order'), self.data(event_date='2020-01-01'))
		self.assertContains(response, 'sm-err-date')
		self.assertFalse(CustomOrderRequest.objects.exists())

	def test_non_image_upload_is_rejected(self):
		bad = SimpleUploadedFile('ref.txt', b'hello', content_type='text/plain')
		response = self.client.post(reverse('shop:custom_order'), self.data(reference_image=bad))
		self.assertContains(response, 'sm-err-file')
		self.assertFalse(CustomOrderRequest.objects.exists())

	def test_honeypot_blocks_bots(self):
		self.client.post(reverse('shop:custom_order'), self.data(website='http://spam'))
		self.assertFalse(CustomOrderRequest.objects.exists())

	@override_settings(ADMIN_ORDER_EMAIL='')
	def test_request_saved_even_without_mail_settings(self):
		self.client.post(reverse('shop:custom_order'), self.data())
		self.assertEqual(CustomOrderRequest.objects.count(), 1)
		self.assertEqual(len(mail.outbox), 0)

	def test_occasion_prefilled_from_link(self):
		response = self.client.get(reverse('shop:custom_order') + '?occasion=entreprise')
		self.assertContains(response, 'value="entreprise" selected')


@override_settings(SECURE_SSL_REDIRECT=False, NEWSLETTER_WELCOME_CODE='BIENVENUE10')
class NewsletterOfferTests(TestCase):
	def test_signup_returns_welcome_code(self):
		response = self.client.post(
			reverse('shop:subscribe_newsletter'),
			data=json.dumps({'email': 'new@example.com'}),
			content_type='application/json',
		)
		self.assertEqual(response.json()['code'], 'BIENVENUE10')
		self.assertTrue(NewsletterUser.objects.filter(email='new@example.com').exists())

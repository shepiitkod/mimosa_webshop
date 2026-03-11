import json
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Order, Product


@override_settings(
	STRIPE_SECRET_KEY='sk_test_dummy',
	STRIPE_WEBHOOK_SECRET='whsec_dummy',
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
			response = self.client.post(reverse('shop:create_checkout_session'))

		self.assertEqual(response.status_code, 302)
		self.assertIn('checkout.stripe.com', response.url)

		created_order = Order.objects.exclude(id=self.order.id).latest('id')
		self.assertEqual(created_order.status, Order.STATUS_PROCESSING)

		with patch('shop.views.stripe.checkout.Session.retrieve') as retrieve_mock:
			retrieve_mock.return_value = {
				'metadata': {'order_id': str(created_order.id)},
				'client_reference_id': str(created_order.id),
			}
			success_response = self.client.get(reverse('shop:success'), {'session_id': 'cs_test_mock'})

		self.assertEqual(success_response.status_code, 200)
		created_order.refresh_from_db()
		self.assertEqual(created_order.status, Order.STATUS_PAID)

	def test_checkout_success_marks_order_paid_from_session(self):
		self.client.login(username='payer', password='test12345')

		with patch('shop.views.stripe.checkout.Session.retrieve') as retrieve_mock:
			retrieve_mock.return_value = {
				'metadata': {'order_id': str(self.order.id)},
				'client_reference_id': str(self.order.id),
			}
			response = self.client.get(reverse('shop:success'), {'session_id': 'cs_test_123'})

		self.assertEqual(response.status_code, 200)
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, Order.STATUS_PAID)

	def test_stripe_webhook_marks_order_paid(self):
		payload = {
			'type': 'checkout.session.completed',
			'data': {
				'object': {
					'metadata': {'order_id': str(self.order.id)},
					'payment_status': 'paid',
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

from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
	CATEGORY_GIFTS = 'Gift Collections'
	CATEGORY_BENTO = 'Bento Candles'
	CATEGORY_SCENTED = 'Scented Candles'

	CATEGORY_CHOICES = [
		(CATEGORY_GIFTS, 'Gift Collections'),
		(CATEGORY_BENTO, 'Bento Candles'),
		(CATEGORY_SCENTED, 'Scented Candles'),
	]

	title = models.CharField(max_length=255)
	description = models.TextField()
	price = models.DecimalField(max_digits=10, decimal_places=2)
	image = models.ImageField(upload_to='products/')
	image_2 = models.ImageField(upload_to='products/', blank=True, null=True)
	image_3 = models.ImageField(upload_to='products/', blank=True, null=True)
	image_4 = models.ImageField(upload_to='products/', blank=True, null=True)
	category = models.CharField(max_length=120, choices=CATEGORY_CHOICES, default=CATEGORY_SCENTED)
	hs_code = models.CharField(max_length=20, blank=True, null=True, default='340600')
	composition = models.CharField(max_length=255, blank=True, default='')
	form_capacity = models.CharField(max_length=120, blank=True, default='')
	wax_type = models.CharField(max_length=120, blank=True, default='')
	# Specs shown on every product detail (Parfum, Mèche, Poids, Temps de combustion)
	scent = models.CharField('Parfum / fragrance', max_length=255, blank=True, default='')
	wick = models.CharField('Mèche / wick', max_length=255, blank=True, default='')
	weight = models.CharField(
		'Poids / weight',
		max_length=120,
		blank=True,
		default='',
		help_text='Displayed on product page (e.g. 200 g, 0.42 kg).',
	)
	burn_time = models.CharField(max_length=120, blank=True, default='')
	stock = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.title


class Order(models.Model):
	STATUS_PROCESSING = 'processing'
	STATUS_SHIPPED = 'shipped'
	STATUS_DELIVERED = 'delivered'
	STATUS_CANCELED = 'canceled'
	STATUS_PAID = 'paid'

	STATUS_CHOICES = [
		(STATUS_PROCESSING, 'В обработке'),
		(STATUS_SHIPPED, 'Отправлен'),
		(STATUS_DELIVERED, 'Доставлен'),
		(STATUS_CANCELED, 'Отменен'),
		(STATUS_PAID, 'Оплачен'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
	created_at = models.DateTimeField(auto_now_add=True)
	total_amount = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PROCESSING)
	
	# Shipping address fields
	shipping_address = models.CharField(max_length=255, blank=True, default='')
	city = models.CharField(max_length=100, blank=True, default='')
	postal_code = models.CharField(max_length=20, blank=True, default='')
	country = models.CharField(max_length=100, blank=True, default='')

	def __str__(self):
		return f'Order #{self.id} - {self.user.username}'


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
	quantity = models.PositiveIntegerField(default=1)
	price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f'{self.product.title} x {self.quantity} (Order #{self.order_id})'


class CartItem(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
	quantity = models.PositiveIntegerField(default=1)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('user', 'product')

	def __str__(self):
		return f'{self.user.username}: {self.product.title} x {self.quantity}'


class NewsletterUser(models.Model):
	email = models.EmailField(unique=True)
	date_added = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-date_added']

	def __str__(self):
		return self.email

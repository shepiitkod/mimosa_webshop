from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField()
	price = models.DecimalField(max_digits=10, decimal_places=2)
	image = models.ImageField(upload_to='products/')
	category = models.CharField(max_length=120)
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

	def __str__(self):
		return f'Order #{self.id} - {self.user.username}'


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
	quantity = models.PositiveIntegerField(default=1)
	price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f'{self.product.title} x {self.quantity} (Order #{self.order_id})'

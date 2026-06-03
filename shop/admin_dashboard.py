from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import NewsletterUser, Order, Product


def _money(value):
	return value or Decimal('0.00')


def _change_label(current, previous, unit=''):
	if previous in (None, 0, Decimal('0.00')):
		if current:
			return 'Новые данные'
		return 'Без изменений'

	difference = current - previous
	if not difference:
		return 'Без изменений'

	sign = '+' if difference > 0 else ''
	return f'{sign}{difference}{unit} к вчера'


def _dashboard_context():
	now = timezone.localtime()
	today = now.date()
	yesterday = today - timedelta(days=1)
	start_date = today - timedelta(days=5)

	today_orders = Order.objects.filter(created_at__date=today).count()
	yesterday_orders = Order.objects.filter(created_at__date=yesterday).count()
	today_paid_revenue = _money(
		Order.objects.filter(created_at__date=today, status=Order.STATUS_PAID).aggregate(total=Sum('total_amount'))['total']
	)
	yesterday_paid_revenue = _money(
		Order.objects.filter(created_at__date=yesterday, status=Order.STATUS_PAID).aggregate(total=Sum('total_amount'))['total']
	)

	active_products = Product.objects.filter(stock__gt=0).count()
	total_products = Product.objects.count()
	new_subscribers_today = NewsletterUser.objects.filter(date_added__date=today).count()
	total_subscribers = NewsletterUser.objects.count()
	total_users = User.objects.count()

	daily_rows = {
		row['day']: {
			'date': row['day'],
			'orders': row['orders'],
			'paid_orders': row['paid_orders'],
			'revenue': _money(row['revenue']),
		}
		for row in (
			Order.objects.filter(created_at__date__gte=start_date)
			.annotate(day=TruncDate('created_at'))
			.values('day')
			.annotate(
				orders=Count('id'),
				paid_orders=Count('id', filter=models.Q(status=Order.STATUS_PAID)),
				revenue=Sum('total_amount', filter=models.Q(status=Order.STATUS_PAID)),
			)
		)
	}

	table_rows = []
	for offset in range(5, -1, -1):
		day = today - timedelta(days=offset)
		table_rows.append(
			daily_rows.get(
				day,
				{
					'date': day,
					'orders': 0,
					'paid_orders': 0,
					'revenue': Decimal('0.00'),
				},
			)
		)

	return {
		'admin_display_name': '',
		'dashboard_stats': [
			{
				'label': 'Заказы сегодня',
				'value': today_orders,
				'counter': today_orders,
				'change': _change_label(today_orders, yesterday_orders),
				'change_class': 'positive' if today_orders >= yesterday_orders else 'negative',
			},
			{
				'label': 'Оплаченная выручка',
				'value': today_paid_revenue,
				'counter': int(today_paid_revenue),
				'suffix': ' грн',
				'change': _change_label(today_paid_revenue, yesterday_paid_revenue, ' грн'),
				'change_class': 'positive' if today_paid_revenue >= yesterday_paid_revenue else 'negative',
			},
			{
				'label': 'Активные товары',
				'value': active_products,
				'counter': active_products,
				'change': f'{active_products} из {total_products} в наличии',
				'change_class': 'neutral',
			},
			{
				'label': 'Подписчики',
				'value': total_subscribers,
				'counter': total_subscribers,
				'change': f'+{new_subscribers_today} сегодня, {total_users} пользователей',
				'change_class': 'positive' if new_subscribers_today else 'neutral',
			},
		],
		'dashboard_table_rows': table_rows,
	}


@staff_member_required
def index(request, extra_context=None):
	context = _dashboard_context()
	context.update(extra_context or {})
	context['admin_display_name'] = request.user.get_full_name() or request.user.username
	return admin.site.index(request, extra_context=context)

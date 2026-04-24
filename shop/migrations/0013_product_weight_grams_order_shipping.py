from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		('shop', '0012_alter_product_weight'),
	]

	operations = [
		migrations.AddField(
			model_name='product',
			name='weight_grams',
			field=models.PositiveIntegerField(
				default=200,
				help_text='Shipping weight in grams (used for checkout).',
			),
		),
		migrations.AddField(
			model_name='order',
			name='shipping_carrier',
			field=models.CharField(blank=True, default='', max_length=32),
		),
		migrations.AddField(
			model_name='order',
			name='shipping_cost',
			field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
		),
		migrations.AddField(
			model_name='order',
			name='shipping_country_code',
			field=models.CharField(blank=True, default='', max_length=2),
		),
	]

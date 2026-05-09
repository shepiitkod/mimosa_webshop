from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('shop', '0013_product_weight_grams_order_shipping'),
	]

	operations = [
		migrations.AlterField(
			model_name='product',
			name='category',
			field=models.CharField(
				choices=[
					('Bento Candles', 'Bento Candles'),
					('Scented Candles', 'Scented Candles'),
					('Decorative Candles', 'Decorative Candles'),
					('Gift Collections', 'Gift Collections'),
				],
				default='Scented Candles',
				max_length=120,
			),
		),
	]


from django.db import migrations, models


LEGACY_CATEGORIES = (
	'Decorative Candles',
	'Decorative Rose',
	'New Arrivals',
)


def forwards_trim_categories(apps, schema_editor):
	Product = apps.get_model('shop', 'Product')
	Product.objects.filter(category__in=LEGACY_CATEGORIES).update(category='Scented Candles')


class Migration(migrations.Migration):

	dependencies = [
		('shop', '0010_product_scent_wick_weight'),
	]

	operations = [
		migrations.RunPython(forwards_trim_categories, migrations.RunPython.noop),
		migrations.AlterField(
			model_name='product',
			name='category',
			field=models.CharField(
				choices=[
					('Gift Collections', 'Gift Collections'),
					('Bento Candles', 'Bento Candles'),
					('Scented Candles', 'Scented Candles'),
				],
				default='Scented Candles',
				max_length=120,
			),
		),
	]

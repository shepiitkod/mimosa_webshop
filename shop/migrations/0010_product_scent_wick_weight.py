from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('shop', '0009_product_hs_code'),
	]

	operations = [
		migrations.AddField(
			model_name='product',
			name='scent',
			field=models.CharField(blank=True, default='', max_length=255, verbose_name='Parfum / fragrance'),
		),
		migrations.AddField(
			model_name='product',
			name='wick',
			field=models.CharField(blank=True, default='', max_length=255, verbose_name='Mèche / wick'),
		),
		migrations.AddField(
			model_name='product',
			name='weight',
			field=models.CharField(blank=True, default='', max_length=120, verbose_name='Poids / weight'),
		),
	]

from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('shop', '0011_trim_product_categories'),
	]

	operations = [
		migrations.AlterField(
			model_name='product',
			name='weight',
			field=models.CharField(
				blank=True,
				default='',
				help_text='Displayed on product page (e.g. 200 g, 0.42 kg).',
				max_length=120,
				verbose_name='Poids / weight',
			),
		),
	]

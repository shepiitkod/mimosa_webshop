from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('shop', '0014_add_decorative_category'),
	]

	operations = [
		migrations.AddField(
			model_name='product',
			name='image_focal_x',
			field=models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)]),
		),
		migrations.AddField(
			model_name='product',
			name='image_focal_y',
			field=models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)]),
		),
		migrations.AddField(
			model_name='product',
			name='image_2_focal_x',
			field=models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)]),
		),
		migrations.AddField(
			model_name='product',
			name='image_2_focal_y',
			field=models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)]),
		),
		migrations.AddField(
			model_name='product',
			name='image_3_focal_x',
			field=models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)]),
		),
		migrations.AddField(
			model_name='product',
			name='image_3_focal_y',
			field=models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)]),
		),
		migrations.AddField(
			model_name='product',
			name='image_4_focal_x',
			field=models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)]),
		),
		migrations.AddField(
			model_name='product',
			name='image_4_focal_y',
			field=models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)]),
		),
	]

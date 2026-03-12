from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_order_address_order_city_order_country_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='address',
            new_name='shipping_address',
        ),
    ]

from django.db.models.signals import post_save
from django.dispatch import receiver

from .image_utils import generate_product_image_variants
from .models import Product


@receiver(post_save, sender=Product)
def optimize_product_images(sender, instance: Product, **kwargs):
    for field_name in ("image", "image_2", "image_3", "image_4"):
        image_field = getattr(instance, field_name, None)
        if image_field:
            generate_product_image_variants(image_field)

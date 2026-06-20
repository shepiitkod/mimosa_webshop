from django import template

from shop.image_utils import product_variant_url

register = template.Library()


@register.filter
def product_i18n_json(product):
    import json

    from django.utils.html import escape

    if not product:
        return ""
    return escape(json.dumps(product.get_i18n_data(), ensure_ascii=False))


@register.inclusion_tag("includes/product_picture.html", takes_context=False)
def product_picture(
    image_field,
    alt="",
    css_class="product-framed-image",
    img_id="",
    w=800,
    h=800,
    loading="lazy",
    fetchpriority="",
    sizes="(max-width: 767px) 100vw, (max-width: 1023px) 50vw, 800px",
    object_position="50% 50%",
):
    srcset_parts = []
    if image_field:
        for width in (400, 800, 1200):
            rel = product_variant_url(image_field, width)
            if rel:
                srcset_parts.append(f"{image_field.storage.url(rel)} {width}w")

    return {
        "src": image_field.url if image_field else "",
        "srcset": ", ".join(srcset_parts),
        "alt": alt,
        "class_name": css_class,
        "img_id": img_id,
        "w": w,
        "h": h,
        "loading": loading,
        "fetchpriority": fetchpriority,
        "sizes": sizes,
        "object_position": object_position,
    }

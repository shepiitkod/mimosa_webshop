from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils.text import slugify

from .models import Product


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'monthly'

    def items(self):
        return ['shop:home', 'shop:about', 'shop:contact']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'bento-candles',
            'scented-candles',
            'decorative-candles',
            'gift-collections',
            'new-arrivals',
        ]

    def location(self, item):
        return reverse('shop:products_by_category', kwargs={'category_slug': item})


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Product.objects.filter(stock__gt=0).order_by('id')

    def location(self, obj):
        return reverse('shop:product_detail', kwargs={
            'product_id': obj.id,
            'slug': slugify(obj.title),
        })

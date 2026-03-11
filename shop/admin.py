from django.contrib import admin
from django.utils.html import format_html

from .models import CartItem, NewsletterUser, Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'category', 'price', 'stock', 'image_preview')
	list_filter = ('category',)
	search_fields = ('title', 'description', 'category', 'composition', 'wax_type')
	fieldsets = (
		('Basic', {'fields': ('title', 'description', 'category', 'price', 'stock')}),
		('Gallery (up to 4 photos)', {'fields': ('image', 'image_2', 'image_3', 'image_4')}),
		('Product Parameters', {'fields': ('composition', 'form_capacity', 'wax_type', 'burn_time')}),
	)
	readonly_fields = ('image_preview', 'image_2_preview', 'image_3_preview', 'image_4_preview')

	def image_preview(self, obj):
		if obj.image:
			return format_html('<img src="{}" style="max-width: 250px; max-height: 250px; border-radius: 4px;" />', obj.image.url)
		return "No image"
	image_preview.short_description = 'Image Preview'

	def image_2_preview(self, obj):
		if obj.image_2:
			return format_html('<img src="{}" style="max-width: 250px; max-height: 250px; border-radius: 4px;" />', obj.image_2.url)
		return "No image"
	image_2_preview.short_description = 'Image 2 Preview'

	def image_3_preview(self, obj):
		if obj.image_3:
			return format_html('<img src="{}" style="max-width: 250px; max-height: 250px; border-radius: 4px;" />', obj.image_3.url)
		return "No image"
	image_3_preview.short_description = 'Image 3 Preview'

	def image_4_preview(self, obj):
		if obj.image_4:
			return format_html('<img src="{}" style="max-width: 250px; max-height: 250px; border-radius: 4px;" />', obj.image_4.url)
		return "No image"
	image_4_preview.short_description = 'Image 4 Preview'

	class Media:
		css = {'all': ('admin_custom.css',)}


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'created_at', 'total_amount', 'status')
	list_filter = ('status', 'created_at')
	search_fields = ('user__username', 'user__email')
	inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ('id', 'order', 'product', 'quantity', 'price_at_purchase')
	search_fields = ('order__id', 'product__title')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'product', 'quantity', 'created_at')
	search_fields = ('user__username', 'product__title')


@admin.register(NewsletterUser)
class NewsletterUserAdmin(admin.ModelAdmin):
	list_display = ('email', 'date_added')
	search_fields = ('email',)
	readonly_fields = ('date_added',)
	ordering = ('-date_added',)

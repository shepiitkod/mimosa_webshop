from django.contrib import admin

from .models import CartItem, Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'category', 'price', 'stock', 'burn_time')
	list_filter = ('category',)
	search_fields = ('title', 'description', 'category', 'composition', 'wax_type')
	fieldsets = (
		('Basic', {'fields': ('title', 'description', 'category', 'price', 'stock')}),
		('Gallery (up to 4 photos)', {'fields': ('image', 'image_2', 'image_3', 'image_4')}),
		('Product Parameters', {'fields': ('composition', 'form_capacity', 'wax_type', 'burn_time')}),
	)


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

from django import forms
from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from decimal import Decimal

from .models import CartItem, NewsletterUser, Order, OrderItem, Product


FRAMING_FIELDS = (
	'image_focal_x',
	'image_focal_y',
	'image_2_focal_x',
	'image_2_focal_y',
	'image_3_focal_x',
	'image_3_focal_y',
	'image_4_focal_x',
	'image_4_focal_y',
)


class ProductAdminForm(forms.ModelForm):
	class Meta:
		model = Product
		fields = '__all__'
		widgets = {
			field_name: forms.HiddenInput(
				attrs={
					'class': 'mimosa-framing-value',
					'data-mimosa-framing-field': field_name,
				}
			)
			for field_name in FRAMING_FIELDS
		}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	form = ProductAdminForm
	change_form_template = 'admin/shop/product/change_form.html'
	class Media:
		css = {'all': ('admin_custom_v2.css', 'image-cropper.css')}
		js = ('image-cropper.js', 'admin_custom_v2.js')

	list_display = ('id', 'title', 'category', 'hs_code', 'price', 'stock', 'image_preview')
	list_filter = ('category',)
	search_fields = (
		'title', 'description', 'category', 'hs_code',
		'composition', 'wax_type', 'scent', 'wick', 'weight',
	)

	fieldsets = (
		('Basic', {'fields': ('title', 'description', 'category', 'hs_code', 'price', 'stock')}),
		(
			'Gallery (up to 4 photos)',
			{
				'fields': (
					'image',
					'image_preview',
					'image_2',
					'image_2_preview',
					'image_3',
					'image_3_preview',
					'image_4',
					'image_4_preview',
					'image_focal_x',
					'image_focal_y',
					'image_2_focal_x',
					'image_2_focal_y',
					'image_3_focal_x',
					'image_3_focal_y',
					'image_4_focal_x',
					'image_4_focal_y',
				)
			},
		),
		(
			'Product Parameters',
			{
				'fields': (
					'scent', 'wick', 'weight', 'weight_grams', 'burn_time',
					'composition', 'form_capacity', 'wax_type',
				),
			},
		),
	)
	readonly_fields = ('image_preview', 'image_2_preview', 'image_3_preview', 'image_4_preview')

	def image_preview(self, obj):
		if obj.image:
			return format_html(
				'<img src="{}" style="width: 96px; height: 120px; object-fit: cover; object-position: {}; border-radius: 8px;" />',
				obj.image.url,
				obj.image_object_position,
			)
		return "No image"
	image_preview.short_description = 'Image Preview'

	def image_2_preview(self, obj):
		if obj.image_2:
			return format_html(
				'<img src="{}" style="width: 96px; height: 120px; object-fit: cover; object-position: {}; border-radius: 8px;" />',
				obj.image_2.url,
				obj.image_2_object_position,
			)
		return "No image"
	image_2_preview.short_description = 'Image 2 Preview'

	def image_3_preview(self, obj):
		if obj.image_3:
			return format_html(
				'<img src="{}" style="width: 96px; height: 120px; object-fit: cover; object-position: {}; border-radius: 8px;" />',
				obj.image_3.url,
				obj.image_3_object_position,
			)
		return "No image"
	image_3_preview.short_description = 'Image 3 Preview'

	def image_4_preview(self, obj):
		if obj.image_4:
			return format_html(
				'<img src="{}" style="width: 96px; height: 120px; object-fit: cover; object-position: {}; border-radius: 8px;" />',
				obj.image_4.url,
				obj.image_4_object_position,
			)
		return "No image"
	image_4_preview.short_description = 'Image 4 Preview'


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	change_list_template = 'admin/shop/order/change_list.html'
	list_display = ('id', 'user', 'total_price', 'shipping_address', 'city', 'postal_code', 'status', 'created_at')
	list_editable = ('status',)
	list_filter = ('status', 'created_at', 'country')
	search_fields = ('id', 'user__username', 'shipping_address', 'city', 'postal_code')
	inlines = [OrderItemInline]
	fieldsets = (
		(
			'Order Info',
			{
				'fields': (
					'user',
					'total_amount',
					'shipping_cost',
					'shipping_carrier',
					'shipping_country_code',
					'status',
					'created_at',
				),
			},
		),
		('Shipping Address', {'fields': ('shipping_address', 'city', 'postal_code', 'country')}),
	)
	readonly_fields = ('created_at',)

	def total_price(self, obj):
		return obj.total_amount

	total_price.short_description = 'Total price'
	total_price.admin_order_field = 'total_amount'

	def address_short(self, obj):
		if obj.shipping_address:
			return f"{obj.shipping_address}"[:50] + ("..." if len(obj.shipping_address) > 50 else "")
		return "-"
	
	address_short.short_description = 'Address'
	address_short.admin_order_field = 'shipping_address'

	def changelist_view(self, request, extra_context=None):
		extra_context = extra_context or {}
		response = super().changelist_view(request, extra_context=extra_context)

		if not hasattr(response, 'context_data'):
			return response

		cl = response.context_data.get('cl')
		if not cl:
			return response

		# Use the filtered changelist queryset so stats match active admin filters/search.
		paid_total = cl.queryset.filter(status=Order.STATUS_PAID).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
		commission = (paid_total * Decimal('0.10')).quantize(Decimal('0.01'))
		client_revenue = (paid_total - commission).quantize(Decimal('0.01'))

		response.context_data['commission_stats'] = {
			'total_revenue': paid_total,
			'my_commission': commission,
			'client_revenue': client_revenue,
		}

		return response


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

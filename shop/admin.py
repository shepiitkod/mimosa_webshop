from decimal import Decimal

from django import forms
from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from .emails import send_order_status_update_email
from .models import CartItem, ContestEntry, NewsletterUser, Order, OrderItem, Product

FRAMING_FIELDS = (
    "image_focal_x",
    "image_focal_y",
    "image_2_focal_x",
    "image_2_focal_y",
    "image_3_focal_x",
    "image_3_focal_y",
)


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            field_name: forms.HiddenInput(
                attrs={
                    "class": "mimosa-framing-value",
                    "data-mimosa-framing-field": field_name,
                }
            )
            for field_name in FRAMING_FIELDS
        }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    change_form_template = "admin/shop/product/change_form.html"

    class Media:
        css = {"all": ("admin_custom_v2.css", "image-cropper.css")}
        js = ("image-cropper.js", "admin_custom_v2.js")

    list_display = (
        "id",
        "title",
        "category",
        "hs_code",
        "price",
        "stock",
        "image_preview",
    )
    list_filter = ("category",)
    search_fields = (
        "title",
        "description",
        "category",
        "hs_code",
        "composition",
        "wax_type",
        "scent",
        "wick",
        "weight",
    )

    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "title",
                    "description",
                    "category",
                    "hs_code",
                    "price",
                    "stock",
                )
            },
        ),
        (
            "Gallery (up to 3 photos)",
            {
                "fields": (
                    "image",
                    "image_preview",
                    "image_2",
                    "image_2_preview",
                    "image_3",
                    "image_3_preview",
                    "image_focal_x",
                    "image_focal_y",
                    "image_2_focal_x",
                    "image_2_focal_y",
                    "image_3_focal_x",
                    "image_3_focal_y",
                )
            },
        ),
        (
            "Product Parameters",
            {
                "fields": (
                    "scent",
                    "wick",
                    "weight",
                    "weight_grams",
                    "burn_time",
                    "composition",
                    "form_capacity",
                    "wax_type",
                ),
            },
        ),
    )
    readonly_fields = ("image_preview", "image_2_preview", "image_3_preview")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 96px; height: 120px; object-fit: cover; object-position: {}; border-radius: 8px;" />',
                obj.image.url,
                obj.image_object_position,
            )
        return "No image"

    image_preview.short_description = "Image Preview"

    def image_2_preview(self, obj):
        if obj.image_2:
            return format_html(
                '<img src="{}" style="width: 96px; height: 120px; object-fit: cover; object-position: {}; border-radius: 8px;" />',
                obj.image_2.url,
                obj.image_2_object_position,
            )
        return "No image"

    image_2_preview.short_description = "Image 2 Preview"

    def image_3_preview(self, obj):
        if obj.image_3:
            return format_html(
                '<img src="{}" style="width: 96px; height: 120px; object-fit: cover; object-position: {}; border-radius: 8px;" />',
                obj.image_3.url,
                obj.image_3_object_position,
            )
        return "No image"

    image_3_preview.short_description = "Image 3 Preview"

    def image_4_preview(self, obj):
        if obj.image_4:
            return format_html(
                '<img src="{}" style="width: 96px; height: 120px; object-fit: cover; object-position: {}; border-radius: 8px;" />',
                obj.image_4.url,
                obj.image_4_object_position,
            )
        return "No image"

    image_4_preview.short_description = "Image 4 Preview"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("color_preview",)
    fields = (
        "product",
        "quantity",
        "price_at_purchase",
        "selected_color_name",
        "selected_color_hex",
        "color_preview",
    )

    def color_preview(self, obj):
        if not obj or not obj.selected_color_name:
            return "—"
        if obj.selected_color_hex:
            return format_html(
                '<span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:14px;height:14px;border-radius:50%;border:1px solid #cdbf9d;background:{};"></span>{}</span>',
                obj.selected_color_hex,
                obj.selected_color_name,
            )
        return obj.selected_color_name

    color_preview.short_description = "Selected color"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "admin/shop/order/change_list.html"
    list_display = (
        "id",
        "user",
        "total_price",
        "shipping_address",
        "city",
        "postal_code",
        "tracking_number",
        "status",
        "status_updated_at",
        "created_at",
    )
    list_editable = ("status",)
    list_filter = ("status", "created_at", "country")
    search_fields = (
        "id",
        "user__username",
        "user__email",
        "shipping_address",
        "city",
        "postal_code",
        "tracking_number",
        "admin_note",
        "items__selected_color_name",
    )
    inlines = [OrderItemInline]
    fieldsets = (
        (
            "Order Info",
            {
                "fields": (
                    "user",
                    "total_amount",
                    "shipping_cost",
                    "shipping_carrier",
                    "shipping_country_code",
                    "tracking_number",
                    "tracking_url",
                    "status",
                    "status_updated_at",
                    "created_at",
                ),
            },
        ),
        (
            "Shipping Address",
            {"fields": ("shipping_address", "city", "postal_code", "country")},
        ),
        (
            "Internal note",
            {
                "fields": ("admin_note",),
                "description": "Private staff note. It is not shown to customers.",
            },
        ),
    )
    readonly_fields = ("created_at", "status_updated_at")

    def total_price(self, obj):
        return obj.total_amount

    total_price.short_description = "Total price"
    total_price.admin_order_field = "total_amount"

    def address_short(self, obj):
        if obj.shipping_address:
            return f"{obj.shipping_address}"[:50] + (
                "..." if len(obj.shipping_address) > 50 else ""
            )
        return "-"

    address_short.short_description = "Address"
    address_short.admin_order_field = "shipping_address"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        response = super().changelist_view(request, extra_context=extra_context)

        if not hasattr(response, "context_data"):
            return response

        cl = response.context_data.get("cl")
        if not cl:
            return response

        # Use the filtered changelist queryset so stats match active admin filters/search.
        paid_total = cl.queryset.filter(status=Order.STATUS_PAID).aggregate(
            total=Sum("total_amount")
        )["total"] or Decimal("0.00")
        commission = (paid_total * Decimal("0.10")).quantize(Decimal("0.01"))
        client_revenue = (paid_total - commission).quantize(Decimal("0.01"))

        response.context_data["commission_stats"] = {
            "total_revenue": paid_total,
            "my_commission": commission,
            "client_revenue": client_revenue,
        }

        return response

    def save_model(self, request, obj, form, change):
        old_status = None
        if change and obj.pk:
            old_status = (
                Order.objects.filter(pk=obj.pk).values_list("status", flat=True).first()
            )
        super().save_model(request, obj, form, change)
        if old_status and old_status != obj.status:
            send_order_status_update_email(obj, old_status=old_status)


@admin.register(ContestEntry)
class ContestEntryAdmin(admin.ModelAdmin):
    """Read-only admin list of orders qualified for the €50 contest draw."""

    list_display = (
        "id",
        "customer_name",
        "customer_email",
        "total_amount",
        "status",
        "shipping_summary",
        "created_at",
    )
    list_filter = ("status", "created_at", "country")
    search_fields = (
        "id",
        "user__username",
        "user__email",
        "shipping_address",
        "city",
        "postal_code",
        "country",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "user",
        "total_amount",
        "status",
        "created_at",
        "shipping_address",
        "city",
        "postal_code",
        "country",
        "shipping_carrier",
        "shipping_cost",
        "shipping_country_code",
        "tracking_number",
        "tracking_url",
        "admin_note",
        "status_updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .filter(total_amount__gte=Decimal("50.00"))
        )

    def customer_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    customer_name.short_description = "Customer"
    customer_name.admin_order_field = "user__username"

    def customer_email(self, obj):
        return obj.user.email or "-"

    customer_email.short_description = "Email"
    customer_email.admin_order_field = "user__email"

    def shipping_summary(self, obj):
        parts = [
            obj.shipping_address,
            obj.city,
            obj.postal_code,
            obj.country,
        ]
        return ", ".join(part for part in parts if part) or "-"

    shipping_summary.short_description = "Delivery information"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price_at_purchase")
    search_fields = ("order__id", "product__title")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "quantity", "created_at")
    search_fields = ("user__username", "product__title")


@admin.register(NewsletterUser)
class NewsletterUserAdmin(admin.ModelAdmin):
    list_display = ("email", "date_added")
    search_fields = ("email",)
    readonly_fields = ("date_added",)
    ordering = ("-date_added",)

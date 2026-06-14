from decimal import Decimal

from django import forms
from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone
from django.utils.html import format_html, format_html_join

from . import shipping
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

PAYMENT_METHOD_LABEL = "Stripe Checkout · card"


def _format_admin_money(value):
    amount = value or Decimal("0.00")
    return f"€{amount:.2f}"


def _customer_display_name(user):
    return (user.get_full_name() or "").strip() or user.username


def _shipping_address_parts(order):
    return [
        part
        for part in [
            order.shipping_address,
            order.city,
            order.postal_code,
            order.country,
        ]
        if part
    ]


def _shipping_summary(order):
    return ", ".join(_shipping_address_parts(order)) or "Address not provided"


def _carrier_name(order):
    carrier_key = (order.shipping_carrier or "").strip().lower()
    if not carrier_key:
        return "Delivery method not selected"
    return shipping.CARRIER_LABELS.get(carrier_key, {}).get(
        "name", carrier_key.replace("_", " ").title()
    )


def _payment_state(order):
    if order.status in {Order.STATUS_PAID, Order.STATUS_SHIPPED, Order.STATUS_DELIVERED}:
        return "Paid via Stripe"
    if order.status == Order.STATUS_CANCELED:
        return "Canceled"
    return "Awaiting Stripe payment"


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
        "order_number",
        "customer_summary",
        "payment_summary",
        "delivery_summary",
        "shipping_method_summary",
        "timeline_summary",
        "status",
    )
    list_display_links = ("order_number",)
    list_editable = ("status",)
    list_filter = ("status", "created_at", "country", "shipping_carrier")
    list_select_related = ("user",)
    list_per_page = 25
    ordering = ("-created_at", "-id")
    date_hierarchy = "created_at"
    search_fields = (
        "id",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "shipping_address",
        "city",
        "postal_code",
        "country",
        "tracking_number",
        "admin_note",
        "items__selected_color_name",
    )
    inlines = [OrderItemInline]
    fieldsets = (
        (
            "Order snapshot",
            {
                "fields": (
                    "order_overview_card",
                    "customer_card",
                    "payment_card",
                    "delivery_card",
                    "timeline_card",
                ),
                "description": "Readable staff overview for packing, payment checks, and customer support.",
            },
        ),
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
    readonly_fields = (
        "order_overview_card",
        "customer_card",
        "payment_card",
        "delivery_card",
        "timeline_card",
        "created_at",
        "status_updated_at",
    )

    class Media:
        css = {"all": ("admin_custom_v2.css",)}

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("items__product")
        )

    def _status_badge(self, obj):
        status = obj.status or Order.STATUS_PROCESSING
        return format_html(
            '<span class="mimosa-order-status mimosa-order-status--{}">{}</span>',
            status,
            obj.get_status_display(),
        )

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

    def order_number(self, obj):
        return format_html(
            '<div class="mimosa-order-cell mimosa-order-number">'
            '<strong>#{}</strong>'
            '<span>{}</span>'
            '<small>{}</small>'
            "</div>",
            obj.id,
            _format_admin_money(obj.total_amount),
            obj.created_at.strftime("%d.%m.%Y %H:%M"),
        )

    order_number.short_description = "Order"
    order_number.admin_order_field = "id"

    def customer_summary(self, obj):
        return format_html(
            '<div class="mimosa-order-cell">'
            "<strong>{}</strong>"
            '<span class="mimosa-order-muted">FIO / client</span>'
            "<small>{}</small>"
            "</div>",
            _customer_display_name(obj.user),
            obj.user.email or obj.user.username,
        )

    customer_summary.short_description = "Customer"
    customer_summary.admin_order_field = "user__username"

    def payment_summary(self, obj):
        return format_html(
            '<div class="mimosa-order-cell">'
            "<strong>{}</strong>"
            '<span>{}</span>'
            "<small>{}</small>"
            "</div>",
            _format_admin_money(obj.total_amount),
            PAYMENT_METHOD_LABEL,
            _payment_state(obj),
        )

    payment_summary.short_description = "Payment"
    payment_summary.admin_order_field = "total_amount"

    def delivery_summary(self, obj):
        return format_html(
            '<div class="mimosa-order-cell mimosa-order-address">'
            "<strong>{}</strong>"
            "<span>{}</span>"
            "</div>",
            obj.city or obj.country or "Destination pending",
            _shipping_summary(obj),
        )

    delivery_summary.short_description = "Address"
    delivery_summary.admin_order_field = "city"

    def shipping_method_summary(self, obj):
        tracking = obj.tracking_number or "No tracking yet"
        return format_html(
            '<div class="mimosa-order-cell">'
            "<strong>{}</strong>"
            "<span>{}</span>"
            "<small>{}</small>"
            "</div>",
            _carrier_name(obj),
            f"Delivery: {_format_admin_money(obj.shipping_cost)}",
            tracking,
        )

    shipping_method_summary.short_description = "Delivery"
    shipping_method_summary.admin_order_field = "shipping_carrier"

    def timeline_summary(self, obj):
        return format_html(
            '<div class="mimosa-order-cell">'
            "<strong>{}</strong>"
            "<span>Created</span>"
            "<small>Status updated: {}</small>"
            "</div>",
            timezone.localtime(obj.created_at).strftime("%d.%m.%Y %H:%M"),
            timezone.localtime(obj.status_updated_at).strftime("%d.%m.%Y %H:%M"),
        )

    timeline_summary.short_description = "Date / time"
    timeline_summary.admin_order_field = "created_at"

    def order_overview_card(self, obj):
        if not obj or not obj.pk:
            return "Save the order first to see the overview."
        item_count = sum(item.quantity for item in obj.items.all())
        return format_html(
            '<div class="mimosa-order-detail-grid">'
            '<section class="mimosa-order-detail-card mimosa-order-detail-card--hero">'
            "<p>Order number</p><strong>#{}</strong><span>{} item(s) · {}</span>"
            "</section>"
            '<section class="mimosa-order-detail-card">'
            "<p>Status</p><strong>{}</strong><span>{}</span>"
            "</section>"
            "</div>",
            obj.id,
            item_count,
            _format_admin_money(obj.total_amount),
            obj.get_status_display(),
            PAYMENT_METHOD_LABEL,
        )

    order_overview_card.short_description = "Order overview"

    def customer_card(self, obj):
        if not obj or not obj.pk:
            return "Save the order first to see customer details."
        return format_html(
            '<div class="mimosa-order-detail-card">'
            "<p>Customer</p><strong>{}</strong>"
            "<span>Email: {}</span><span>Username: {}</span>"
            "</div>",
            _customer_display_name(obj.user),
            obj.user.email or "-",
            obj.user.username,
        )

    customer_card.short_description = "FIO / customer"

    def payment_card(self, obj):
        if not obj or not obj.pk:
            return "Save the order first to see payment details."
        return format_html(
            '<div class="mimosa-order-detail-card">'
            "<p>Payment</p><strong>{}</strong>"
            "<span>Method: {}</span><span>Payment: {}</span><span>Order status: {}</span><span>Shipping: {}</span>"
            "</div>",
            _format_admin_money(obj.total_amount),
            PAYMENT_METHOD_LABEL,
            _payment_state(obj),
            obj.get_status_display(),
            _format_admin_money(obj.shipping_cost),
        )

    payment_card.short_description = "Payment details"

    def delivery_card(self, obj):
        if not obj or not obj.pk:
            return "Save the order first to see delivery details."
        tracking_html = (
            format_html(
                '<a href="{}" target="_blank" rel="noopener">{}</a>',
                obj.tracking_url,
                obj.tracking_number,
            )
            if obj.tracking_url and obj.tracking_number
            else obj.tracking_number or "-"
        )
        return format_html(
            '<div class="mimosa-order-detail-card">'
            "<p>Delivery</p><strong>{}</strong>"
            "<span>Address: {}</span><span>Country code: {}</span><span>Tracking: {}</span>"
            "</div>",
            _carrier_name(obj),
            _shipping_summary(obj),
            obj.shipping_country_code or "-",
            tracking_html,
        )

    delivery_card.short_description = "Address / delivery"

    def timeline_card(self, obj):
        if not obj or not obj.pk:
            return "Save the order first to see date and time."
        created = timezone.localtime(obj.created_at).strftime("%d.%m.%Y %H:%M")
        updated = timezone.localtime(obj.status_updated_at).strftime("%d.%m.%Y %H:%M")
        rows = [
            ("Created", created),
            ("Status updated", updated),
        ]
        return format_html(
            '<div class="mimosa-order-detail-card">'
            "<p>Date and time</p>{}</div>",
            format_html_join(
                "",
                "<span><strong>{}</strong>: {}</span>",
                rows,
            ),
        )

    timeline_card.short_description = "Date / time"

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

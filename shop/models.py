from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

IMAGE_FOCAL_POINT_VALIDATORS = [MinValueValidator(0), MaxValueValidator(100)]


class Product(models.Model):
    CATEGORY_GIFTS = "Gift Collections"
    CATEGORY_BENTO = "Bento Candles"
    CATEGORY_SCENTED = "Scented Candles"
    CATEGORY_DECORATIVE = "Decorative Candles"
    CATEGORY_CEREMONY = "Ceremony Candles"
    CATEGORY_CEREMONY_LEGACY = "Bougies de cérémonie"
    CATEGORY_SACHETS = "Plaster Sachets"

    CATEGORY_CHOICES = [
        (CATEGORY_BENTO, "Bento Candles"),
        (CATEGORY_SCENTED, "Scented Candles"),
        (CATEGORY_DECORATIVE, "Decorative Candles"),
        (CATEGORY_GIFTS, "Gift Collections"),
        (CATEGORY_CEREMONY, "Ceremony Candles"),
        (CATEGORY_CEREMONY_LEGACY, "Ceremony Candles"),
        (CATEGORY_SACHETS, "Plaster Sachets"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/")
    image_2 = models.ImageField(upload_to="products/", blank=True, null=True)
    image_3 = models.ImageField(upload_to="products/", blank=True, null=True)
    image_4 = models.ImageField(upload_to="products/", blank=True, null=True)
    image_focal_x = models.PositiveSmallIntegerField(
        default=50, validators=IMAGE_FOCAL_POINT_VALIDATORS
    )
    image_focal_y = models.PositiveSmallIntegerField(
        default=50, validators=IMAGE_FOCAL_POINT_VALIDATORS
    )
    image_2_focal_x = models.PositiveSmallIntegerField(
        default=50, validators=IMAGE_FOCAL_POINT_VALIDATORS
    )
    image_2_focal_y = models.PositiveSmallIntegerField(
        default=50, validators=IMAGE_FOCAL_POINT_VALIDATORS
    )
    image_3_focal_x = models.PositiveSmallIntegerField(
        default=50, validators=IMAGE_FOCAL_POINT_VALIDATORS
    )
    image_3_focal_y = models.PositiveSmallIntegerField(
        default=50, validators=IMAGE_FOCAL_POINT_VALIDATORS
    )
    image_4_focal_x = models.PositiveSmallIntegerField(
        default=50, validators=IMAGE_FOCAL_POINT_VALIDATORS
    )
    image_4_focal_y = models.PositiveSmallIntegerField(
        default=50, validators=IMAGE_FOCAL_POINT_VALIDATORS
    )
    category = models.CharField(
        max_length=120, choices=CATEGORY_CHOICES, default=CATEGORY_SCENTED
    )
    hs_code = models.CharField(max_length=20, blank=True, null=True, default="340600")
    composition = models.CharField(max_length=255, blank=True, default="")
    form_capacity = models.CharField(max_length=120, blank=True, default="")
    wax_type = models.CharField(max_length=120, blank=True, default="")
    # Specs shown on every product detail (Parfum, Mèche, Poids, Temps de combustion)
    scent = models.CharField(
        "Parfum / fragrance", max_length=255, blank=True, default=""
    )
    wick = models.CharField("Mèche / wick", max_length=255, blank=True, default="")
    weight = models.CharField(
        "Poids / weight",
        max_length=120,
        blank=True,
        default="",
        help_text="Displayed on product page (e.g. 200 g, 0.42 kg).",
    )
    weight_grams = models.PositiveIntegerField(
        default=200,
        help_text="Shipping weight in grams (used for checkout).",
    )
    burn_time = models.CharField(max_length=120, blank=True, default="")
    stock = models.PositiveIntegerField(default=0)
    i18n = models.JSONField(default=dict, blank=True)

    I18N_FIELDS = (
        "title",
        "description",
        "scent",
        "wick",
        "burn_time",
        "composition",
        "form_capacity",
        "wax_type",
    )

    def __str__(self):
        return self.title

    def get_i18n_data(self) -> dict:
        from .translation_service import I18N_FIELDS, SUPPORTED_LANGS, _fallback_i18n, _source_payload

        payload = _source_payload(self)
        stored = self.i18n if isinstance(self.i18n, dict) else {}
        result = {}

        for lang in SUPPORTED_LANGS:
            lang_data = stored.get(lang)
            if isinstance(lang_data, dict):
                result[lang] = {
                    field: str(lang_data.get(field, payload.get(field, ""))).strip()
                    for field in I18N_FIELDS
                }
            else:
                result[lang] = dict(payload)

        if not any(payload.values()):
            return _fallback_i18n(payload)
        return result

    @property
    def category_translation_key(self):
        return {
            self.CATEGORY_BENTO: "nav-sub-bento",
            self.CATEGORY_SCENTED: "nav-sub-scented",
            self.CATEGORY_DECORATIVE: "nav-sub-decorative",
            self.CATEGORY_GIFTS: "nav-sub-gifts",
            self.CATEGORY_CEREMONY: "nav-sub-ceremony",
            self.CATEGORY_CEREMONY_LEGACY: "nav-sub-ceremony",
            self.CATEGORY_SACHETS: "nav-sub-sachets",
        }.get(self.category, "")

    @property
    def category_display_name(self):
        return {
            self.CATEGORY_BENTO: "Bento Candles",
            self.CATEGORY_SCENTED: "Scented Candles",
            self.CATEGORY_DECORATIVE: "Decorative Candles",
            self.CATEGORY_GIFTS: "Gift Collections",
            self.CATEGORY_CEREMONY: "Ceremony Candles",
            self.CATEGORY_CEREMONY_LEGACY: "Ceremony Candles",
            self.CATEGORY_SACHETS: "Plaster Sachets",
        }.get(self.category, self.category)

    @property
    def image_object_position(self):
        return f"{self.image_focal_x}% {self.image_focal_y}%"

    @property
    def image_2_object_position(self):
        return f"{self.image_2_focal_x}% {self.image_2_focal_y}%"

    @property
    def image_3_object_position(self):
        return f"{self.image_3_focal_x}% {self.image_3_focal_y}%"

    @property
    def image_4_object_position(self):
        return f"{self.image_4_focal_x}% {self.image_4_focal_y}%"


class Order(models.Model):
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELED = "canceled"
    STATUS_PAID = "paid"

    STATUS_CHOICES = [
        (STATUS_PROCESSING, "В обработке"),
        (STATUS_SHIPPED, "Отправлен"),
        (STATUS_DELIVERED, "Доставлен"),
        (STATUS_CANCELED, "Отменен"),
        (STATUS_PAID, "Оплачен"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PROCESSING
    )

    # Shipping address fields
    shipping_address = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    postal_code = models.CharField(max_length=20, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="")
    shipping_carrier = models.CharField(max_length=32, blank=True, default="")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_country_code = models.CharField(max_length=2, blank=True, default="")
    tracking_number = models.CharField(max_length=120, blank=True, default="")
    tracking_url = models.URLField(max_length=500, blank=True, default="")
    admin_note = models.TextField(blank=True, default="")
    status_updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = (
                type(self)
                .objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )
            if old_status and old_status != self.status:
                self.status_updated_at = timezone.now()
                update_fields = kwargs.get("update_fields")
                if update_fields is not None:
                    kwargs["update_fields"] = set(update_fields) | {"status_updated_at"}
        elif not self.status_updated_at:
            self.status_updated_at = timezone.now()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    selected_color_name = models.CharField(max_length=80, blank=True, default="")
    selected_color_hex = models.CharField(max_length=16, blank=True, default="")

    def __str__(self):
        color = f" / {self.selected_color_name}" if self.selected_color_name else ""
        return f"{self.product.title}{color} x {self.quantity} (Order #{self.order_id})"


class ContestEntry(Order):
    class Meta:
        proxy = True
        verbose_name = "Contest entry"
        verbose_name_plural = "Contest entries"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username}: {self.product.title} x {self.quantity}"


class NewsletterUser(models.Model):
    email = models.EmailField(unique=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_added"]

    def __str__(self):
        return self.email

import json
import re
import traceback
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Count, Prefetch, Sum
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import shipping
from .ai_service import (
    generate_chat_reply,
    generate_product_form_fields,
    sanitize_history,
    stream_sse_events,
    wants_product_form_fill,
)
from .emails import (
    send_admin_order_notification,
    send_order_confirmation_email,
    send_order_status_update_email,
)
from .models import CartItem, NewsletterUser, Order, OrderItem, Product

CATEGORY_SLUG_ALIASES = {
    "decorative-rose": "scented-candles",
    "new-arrivals": "scented-candles",
    "bougies-de-ceremonie": "ceremony-candles",
}

COLOR_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def _format_money(value) -> str:
    try:
        amount = Decimal(value or 0).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        amount = Decimal("0.00")
    return f"€{amount}"


def _build_admin_copilot_context(prompt: str) -> str:
    """Return a compact live admin snapshot for staff-only AI answers."""
    users = list(User.objects.order_by("username")[:80])
    admin_users = list(User.objects.filter(is_staff=True).order_by("username")[:80])
    products = list(Product.objects.order_by("title")[:80])
    orders = list(
        Order.objects.select_related("user")
        .prefetch_related(
            Prefetch("items", queryset=OrderItem.objects.select_related("product"))
        )
        .order_by("-created_at")[:40]
    )
    contest_orders = list(
        Order.objects.select_related("user")
        .filter(total_amount__gte=Decimal("50.00"))
        .order_by("-created_at")[:60]
    )
    newsletter_users = list(NewsletterUser.objects.order_by("-date_added")[:40])
    cart_items = list(
        CartItem.objects.select_related("user", "product").order_by("-created_at")[:40]
    )

    user_total = User.objects.count()
    staff_total = User.objects.filter(is_staff=True).count()
    superuser_total = User.objects.filter(is_superuser=True).count()
    active_total = User.objects.filter(is_active=True).count()
    product_total = Product.objects.count()
    order_total = Order.objects.count()
    contest_total = Order.objects.filter(total_amount__gte=Decimal("50.00")).count()
    newsletter_total = NewsletterUser.objects.count()
    cart_item_total = CartItem.objects.count()

    status_counts = {
        row["status"]: row["total"]
        for row in Order.objects.values("status").annotate(total=Count("id"))
    }
    category_counts = {
        row["category"]: row["total"]
        for row in Product.objects.values("category").annotate(total=Count("id"))
    }

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    def _order_metrics_since(start):
        qs = Order.objects.filter(created_at__gte=start)
        return {
            "count": qs.count(),
            "amount": qs.aggregate(total=Sum("total_amount"))["total"] or Decimal("0"),
        }

    today_metrics = _order_metrics_since(today_start)
    week_metrics = _order_metrics_since(week_start)
    month_metrics = _order_metrics_since(month_start)
    unpaid_orders = Order.objects.filter(
        status__in=[Order.STATUS_PROCESSING]
    ).count()
    paid_orders = Order.objects.filter(status=Order.STATUS_PAID).count()
    shipped_orders = Order.objects.filter(status=Order.STATUS_SHIPPED).count()
    delivered_orders = Order.objects.filter(status=Order.STATUS_DELIVERED).count()
    canceled_orders = Order.objects.filter(status=Order.STATUS_CANCELED).count()
    top_products = (
        OrderItem.objects.values("product__id", "product__title")
        .annotate(quantity=Sum("quantity"), revenue=Sum("price_at_purchase"))
        .order_by("-quantity")[:10]
    )

    revenue = sum((order.total_amount or Decimal("0")) for order in orders)
    all_revenue = sum(
        (row.total_amount or Decimal("0"))
        for row in Order.objects.only("total_amount").iterator()
    )
    inventory_units = sum(product.stock or 0 for product in products)
    cart_units = sum(item.quantity or 0 for item in cart_items)

    lines = [
        "<admin_database_context>",
        "This is a live staff-only snapshot from the MIMOSA Django admin database.",
        "Use it to answer directly. If the answer is present here, do not tell the user to look it up manually.",
        f"User request: {prompt[:700]}",
        "",
        "SUMMARY:",
        f"- Users: total={user_total}, active={active_total}, staff/admin={staff_total}, superusers={superuser_total}",
        f"- Products: total={product_total}, visible_sample={len(products)}, sample_stock_units={inventory_units}",
        f"- Orders: total={order_total}, recent_sample={len(orders)}, all_time_total_amount={_format_money(all_revenue)}, recent_sample_amount={_format_money(revenue)}",
        f"- Contest entries (€50+ orders): total={contest_total}, visible_sample={len(contest_orders)}",
        f"- Newsletter subscribers: total={newsletter_total}",
        f"- Cart rows: total={cart_item_total}, recent_sample_qty={cart_units}",
        f"- Order status counts: {status_counts or {}}",
        f"- Product category counts: {category_counts or {}}",
        "",
        "ANALYTICS:",
        f"- Today: orders={today_metrics['count']}, amount={_format_money(today_metrics['amount'])}",
        f"- Last 7 days: orders={week_metrics['count']}, amount={_format_money(week_metrics['amount'])}",
        f"- Last 30 days: orders={month_metrics['count']}, amount={_format_money(month_metrics['amount'])}",
        f"- Pipeline: unpaid/processing={unpaid_orders}, paid={paid_orders}, shipped={shipped_orders}, delivered={delivered_orders}, canceled={canceled_orders}",
        "- Top products by quantity: "
        + (
            "; ".join(
                f"{row['product__title']} (qty={row['quantity']}, revenue={_format_money(row['revenue'] or 0)})"
                for row in top_products
            )
            or "no order item data"
        ),
        "",
        "USERS:",
    ]

    for user in users:
        flags = []
        if user.is_superuser:
            flags.append("superuser")
        if user.is_staff:
            flags.append("staff")
        if not user.is_active:
            flags.append("inactive")
        full_name = (user.get_full_name() or "").strip()
        lines.append(
            f"- id={user.id}; username={user.username}; email={user.email or '-'}; name={full_name or '-'}; flags={','.join(flags) or 'customer'}; joined={user.date_joined:%Y-%m-%d}"
        )

    lines.append("")
    lines.append("STAFF / ADMIN USERS:")
    for user in admin_users:
        role = "superuser" if user.is_superuser else "staff"
        full_name = (user.get_full_name() or "").strip()
        lines.append(
            f"- id={user.id}; username={user.username}; email={user.email or '-'}; name={full_name or '-'}; role={role}; active={user.is_active}"
        )

    lines.append("")
    lines.append("PRODUCTS:")
    for product in products:
        lines.append(
            f"- id={product.id}; title={product.title}; category={product.category}; price={_format_money(product.price)}; stock={product.stock}; scent={product.scent or '-'}; weight={product.weight or '-'}"
        )

    low_stock = [p for p in products if (p.stock or 0) <= 3]
    if low_stock:
        lines.append("")
        lines.append("LOW STOCK PRODUCTS (sample, stock <= 3):")
        for product in low_stock[:20]:
            lines.append(f"- id={product.id}; {product.title}; stock={product.stock}")

    lines.append("")
    lines.append("RECENT ORDERS:")
    for order in orders:
        item_bits = [
            f"{item.product.title}{f' color={item.selected_color_name}' if item.selected_color_name else ''} x{item.quantity} ({_format_money(item.price_at_purchase)})"
            for item in order.items.all()
        ]
        shipping = ", ".join(
            part
            for part in [
                order.shipping_address,
                order.city,
                order.postal_code,
                order.country,
            ]
            if part
        )
        lines.append(
            f"- id={order.id}; user={order.user.username}; email={order.user.email or '-'}; status={order.status}; total={_format_money(order.total_amount)}; date={order.created_at:%Y-%m-%d}; tracking_number={order.tracking_number or '-'}; tracking_url={order.tracking_url or '-'}; admin_note={order.admin_note or '-'}; shipping={shipping or '-'}; items={'; '.join(item_bits) or '-'}"
        )

    lines.append("")
    lines.append("CONTEST ENTRIES (€50+ ORDERS):")
    for order in contest_orders:
        shipping = ", ".join(
            part
            for part in [
                order.shipping_address,
                order.city,
                order.postal_code,
                order.country,
            ]
            if part
        )
        customer_name = order.user.get_full_name() or order.user.username
        lines.append(
            f"- order_id={order.id}; customer={customer_name}; username={order.user.username}; email={order.user.email or '-'}; total={_format_money(order.total_amount)}; status={order.status}; delivery={shipping or '-'}"
        )

    lines.append("")
    lines.append("RECENT NEWSLETTER SUBSCRIBERS:")
    for subscriber in newsletter_users:
        lines.append(
            f"- id={subscriber.id}; email={subscriber.email}; date={subscriber.date_added:%Y-%m-%d}"
        )

    lines.append("")
    lines.append("RECENT CART ITEMS:")
    for item in cart_items:
        lines.append(
            f"- user={item.user.username}; product={item.product.title}; quantity={item.quantity}; created={item.created_at:%Y-%m-%d}"
        )

    lines.append("</admin_database_context>")
    return "\n".join(lines)


def _get_validated_stripe_secret_key() -> str:
    """Return configured Stripe secret key and enforce Live key in production."""
    secret_key = (settings.STRIPE_SECRET_KEY or "").strip()
    if not secret_key:
        raise ValueError("Stripe secret key is not configured.")
    if not secret_key.startswith("sk_"):
        raise ValueError("Stripe secret key has invalid format.")
    if not settings.DEBUG and not secret_key.startswith("sk_live_"):
        raise ValueError(
            "Stripe Live mode requires STRIPE_SECRET_KEY starting with sk_live_."
        )
    return secret_key


def _to_cents(amount: Decimal) -> int:
    try:
        normalized = Decimal(amount).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        raise ValueError("Invalid order amount")

    cents = int(normalized * 100)
    if cents <= 0:
        raise ValueError("Order amount must be greater than zero")
    return cents


def _build_site_url(path: str) -> str:
    base_url = (settings.SITE_URL or "").rstrip("/")
    if not base_url:
        raise ValueError("Site URL is not configured.")
    return f"{base_url}{path}"


def _create_stripe_session_for_order(request, order):
    stripe.api_key = _get_validated_stripe_secret_key()
    order_items = list(order.items.select_related("product").all())
    customer_email = (getattr(request.user, "email", "") or "").strip()

    if not order_items:
        raise ValueError("Cannot create a Stripe session for an order with no items.")

    hs_codes = sorted({(item.product.hs_code or "340600") for item in order_items})

    # build_absolute_uri on Render (behind a TLS-terminating proxy) returns http://.
    # Stripe Live mode requires https://, so we force it.
    def _https(url: str) -> str:
        return (
            url.replace("http://", "https://", 1) if url.startswith("http://") else url
        )

    success_url = (
        _https(_build_site_url(reverse("shop:success")))
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = _https(_build_site_url(reverse("shop:cancel")))

    def _stripe_item_name(item):
        if item.selected_color_name:
            return f"{item.product.title} — Color: {item.selected_color_name}"
        return item.product.title

    line_items = [
        {
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": _stripe_item_name(item),
                },
                "unit_amount": int(round(item.product.price * 100)),
            },
            "quantity": item.quantity,
        }
        for item in order_items
    ]

    ship = getattr(order, "shipping_cost", None) or Decimal("0")
    if ship > 0:
        carrier_key = (order.shipping_carrier or "").strip().lower()
        c_meta = shipping.CARRIER_LABELS.get(carrier_key, {})
        ship_label = c_meta.get("name", "Livraison")
        line_items.append(
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": f"Livraison — {ship_label}"},
                    "unit_amount": int((ship * Decimal("100")).quantize(Decimal("1"))),
                },
                "quantity": 1,
            }
        )

    allow_promotion_codes = True

    shipping_iso = (getattr(order, "shipping_country_code", "") or "").strip().upper()
    session_metadata = {
        "order_id": str(order.id),
        "hs_codes": ",".join(hs_codes),
        "primary_hs_code": hs_codes[0] if hs_codes else "340600",
        "shipping_carrier": (order.shipping_carrier or ""),
        "shipping_country": shipping_iso,
    }

    create_kwargs = {
        "client_reference_id": str(order.id),
        "metadata": session_metadata,
        "line_items": line_items,
        "mode": "payment",
        "payment_method_types": ["card"],
        "allow_promotion_codes": allow_promotion_codes,
        "billing_address_collection": "auto",
        "shipping_address_collection": {
            "allowed_countries": shipping.stripe_shipping_countries()
        },
        "success_url": success_url,
        "cancel_url": cancel_url,
    }

    # Do not pass discounts when allow_promotion_codes=True.
    if customer_email:
        create_kwargs["customer_email"] = customer_email

    return stripe.checkout.Session.create(
        idempotency_key=f"order_checkout_{order.id}",
        **create_kwargs,
    )


def _amount_total_to_decimal(session_data) -> Optional[Decimal]:
    """Return Stripe amount_total in Decimal major units (e.g., EUR), if available."""
    if not session_data or not hasattr(session_data, "get"):
        return None

    amount_total = session_data.get("amount_total")
    if amount_total is None:
        return None

    try:
        return (Decimal(str(amount_total)) / Decimal("100")).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _mark_order_paid_from_checkout_session(session_id: str) -> bool:
    if not session_id:
        return False

    try:
        stripe.api_key = _get_validated_stripe_secret_key()
    except ValueError:
        return False

    try:
        session_data = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        return False

    metadata = session_data.get("metadata", {}) if hasattr(session_data, "get") else {}
    order_id = metadata.get("order_id") if metadata else None
    if not order_id and hasattr(session_data, "get"):
        order_id = session_data.get("client_reference_id")

    if not order_id:
        return False

    try:
        order = Order.objects.get(id=order_id)
    except (Order.DoesNotExist, ValueError, TypeError):
        return False

    updated_fields = []

    # Persist final Stripe amount (after promo codes/discounts) to the order.
    final_amount = _amount_total_to_decimal(session_data)
    if final_amount is not None and order.total_amount != final_amount:
        order.total_amount = final_amount
        updated_fields.append("total_amount")

    # Persist shipping details coming from Stripe Checkout.
    shipping_details = session_data.get("shipping_details")
    if shipping_details and shipping_details.get("address"):
        address_data = shipping_details.get("address")
        order.shipping_address = address_data.get("line1", "")
        order.city = address_data.get("city", "")
        order.postal_code = address_data.get("postal_code", "")
        order.country = address_data.get("country", "")
        updated_fields.extend(["shipping_address", "city", "postal_code", "country"])

    if order.status != Order.STATUS_PAID:
        order.status = Order.STATUS_PAID
        updated_fields.append("status")

    if updated_fields:
        order.save(update_fields=sorted(set(updated_fields)))
        if "status" in updated_fields:
            _decrement_stock_for_order(order.id)
            send_order_confirmation_email(order)
            send_admin_order_notification(order)

    return True


def _decrement_stock_for_order(order_id: int) -> None:
    """Atomically decrement product stock for a paid order. Safe to call multiple times (idempotent)."""
    try:
        with transaction.atomic():
            items = (
                OrderItem.objects.filter(order_id=order_id)
                .select_related("product")
                .select_for_update()
            )
            for item in items:
                product = item.product
                new_stock = max(0, product.stock - item.quantity)
                Product.objects.filter(id=product.id, stock__gt=0).update(
                    stock=new_stock
                )
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(
            "Stock decrement failed for order %s: %s", order_id, e
        )


def _get_cart(session):
    return session.setdefault("cart", {})


def _cart_count(session) -> int:
    total = 0
    for raw in _get_cart(session).values():
        if isinstance(raw, dict):
            raw = raw.get("quantity", 0)
        try:
            total += int(raw)
        except (TypeError, ValueError):
            continue
    return total


def _cart_key(product_id: int, color_name: str = "") -> str:
    color_slug = slugify(color_name or "")
    return f"{product_id}:{color_slug}" if color_slug else str(product_id)


def _clean_color_hex(value: str) -> str:
    value = (value or "").strip()
    return value if COLOR_HEX_RE.match(value) else ""


def _cart_product_id(cart_key: str) -> Optional[int]:
    try:
        return int(str(cart_key).split(":", 1)[0])
    except (TypeError, ValueError):
        return None


def _cart_entry(raw) -> dict[str, object]:
    if isinstance(raw, dict):
        try:
            quantity = int(raw.get("quantity", 0))
        except (TypeError, ValueError):
            quantity = 0
        return {
            "quantity": quantity,
            "selected_color_name": str(raw.get("selected_color_name") or "").strip(),
            "selected_color_hex": _clean_color_hex(str(raw.get("selected_color_hex") or "")),
        }
    try:
        quantity = int(raw)
    except (TypeError, ValueError):
        quantity = 0
    return {"quantity": quantity, "selected_color_name": "", "selected_color_hex": ""}


def _cart_summary(session):
    cart = _get_cart(session)
    if not cart:
        return [], Decimal("0.00")

    product_ids = [pid for pid in (_cart_product_id(key) for key in cart.keys()) if pid]
    products = Product.objects.filter(id__in=product_ids)
    products_map = {product.id: product for product in products}

    items = []
    total = Decimal("0.00")

    for cart_key, raw_entry in cart.items():
        product_id = _cart_product_id(cart_key)
        if not product_id:
            continue
        entry = _cart_entry(raw_entry)
        product = products_map.get(product_id)
        if not product:
            continue
        qty = max(1, int(entry["quantity"]))
        line_total = (product.price * qty).quantize(Decimal("0.01"))
        total += line_total
        items.append(
            {
                "cart_key": cart_key,
                "product": product,
                "quantity": qty,
                "line_total": line_total,
                "selected_color_name": entry["selected_color_name"],
                "selected_color_hex": entry["selected_color_hex"],
            }
        )

    return items, total.quantize(Decimal("0.01"))


def _cart_total_weight_grams(items) -> int:
    total = 0
    for item in items:
        w = int(getattr(item["product"], "weight_grams", 200) or 200)
        total += w * int(item["quantity"])
    return max(total, 1)


@require_GET
def index_view(request):
    # Home: show the three most recently added products (by id) under "Our New Collection".
    products = Product.objects.all().order_by("-id")[:3]
    cart_count = _cart_count(request.session)
    return render(
        request, "index.html", {"products": products, "cart_count": cart_count}
    )


@require_GET
def products_catalog_view(request, category_slug=None):
    if category_slug in CATEGORY_SLUG_ALIASES:
        return redirect(
            "shop:products_by_category",
            category_slug=CATEGORY_SLUG_ALIASES[category_slug],
            permanent=True,
        )

    products_qs = Product.objects.all().order_by("title")
    raw_counts = Product.objects.values("category").annotate(total=Count("id"))
    counts_map = {}
    for row in raw_counts:
        category = row["category"]
        canonical = (
            Product.CATEGORY_CEREMONY
            if category == Product.CATEGORY_CEREMONY_LEGACY
            else category
        )
        counts_map[canonical] = counts_map.get(canonical, 0) + row["total"]

    visible_categories = (
        Product.CATEGORY_BENTO,
        Product.CATEGORY_SCENTED,
        Product.CATEGORY_DECORATIVE,
        Product.CATEGORY_CEREMONY,
    )

    category_items = []
    for name in visible_categories:
        category_items.append(
            {
                "name": Product(category=name).category_display_name,
                "slug": slugify(name),
                "count": counts_map.get(name, 0),
                "translate_key": Product(category=name).category_translation_key,
                "filter_values": (
                    [Product.CATEGORY_CEREMONY, Product.CATEGORY_CEREMONY_LEGACY]
                    if name == Product.CATEGORY_CEREMONY
                    else [name]
                ),
            }
        )

    active_category = None
    if category_slug:
        active_category = next(
            (item for item in category_items if item["slug"] == category_slug), None
        )
        if active_category:
            products_qs = products_qs.filter(
                category__in=active_category["filter_values"]
            )

    total_products_count = Product.objects.count()

    cart_count = _cart_count(request.session)
    return render(
        request,
        "products_catalog.html",
        {
            "products": products_qs,
            "total_products_count": total_products_count,
            "categories": category_items,
            "active_category": active_category,
            "cart_count": cart_count,
        },
    )


@require_GET
def product_detail_view(request, product_id, slug=None):
    product = get_object_or_404(Product, id=product_id)
    canonical_slug = slugify(product.title)
    if slug != canonical_slug:
        return redirect(
            "shop:product_detail", product_id=product.id, slug=canonical_slug
        )

    related_products = (
        Product.objects.filter(category=product.category)
        .exclude(id=product.id)
        .order_by("title")[:4]
    )

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "canonical_slug": canonical_slug,
            "related_products": related_products,
        },
    )


@require_GET
def seconde_vie_view(request):
    """Landing page for the Candle Upcycling (Seconde vie) premium service."""
    return render(request, "seconde_vie.html")


@require_GET
def about_view(request):
    return render(request, "About.html")


@require_GET
def contact_view(request):
    return render(request, "contact.html")


@require_GET
def confidential_view(request):
    return render(request, "confidential.html")


@require_GET
def product_bento_view(request):
    """Legacy URL /products/bento/ — serve the live Bento category from the catalogue."""
    return redirect(
        "shop:products_by_category", category_slug=slugify(Product.CATEGORY_BENTO)
    )


@require_GET
def product_rose_view(request):
    """Legacy decorative product page URL — catalogue now has three categories only."""
    return redirect("shop:products_by_category", category_slug="scented-candles")


@require_GET
def login_view(request):
    form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


@require_POST
def login_submit(request):
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        login(request, form.get_user())
        return redirect("shop:profile")
    return render(request, "registration/login.html", {"form": form})


@require_GET
def register_view(request):
    form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@require_POST
def register_submit(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("shop:profile")
    return render(request, "registration/register.html", {"form": form})


@require_GET
def logout_view(request):
    logout(request)
    return redirect("shop:home")


@login_required
@require_GET
def profile_view(request):
    import logging

    logger = logging.getLogger(__name__)
    try:
        orders = list(
            Order.objects.filter(user=request.user)
            .prefetch_related(
                Prefetch("items", queryset=OrderItem.objects.select_related("product"))
            )
            .order_by("-created_at")
        )
    except Exception as e:
        logger.error("profile_view orders query failed: %s", e, exc_info=True)
        orders = []

    try:
        from decimal import Decimal

        total_spent = sum((o.total_amount or Decimal("0")) for o in orders)
    except Exception as e:
        logger.error("profile_view total_spent failed: %s", e, exc_info=True)
        total_spent = 0

    try:
        cart_count = _cart_count(request.session)
    except Exception as e:
        logger.error("profile_view cart_count failed: %s", e, exc_info=True)
        cart_count = 0

    user = request.user
    display_name = (user.get_full_name() or "").strip() or user.username
    user_initial = (user.username[:1] or "?").upper()

    return render(
        request,
        "profile.html",
        {
            "orders": orders,
            "orders_count": len(orders),
            "total_spent": total_spent,
            "cart_count": cart_count,
            "user_display_name": display_name,
            "user_initial": user_initial,
        },
    )


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1) or 1)
    update = request.POST.get("update") == "1"
    selected_color_name = (request.POST.get("selected_color_name") or "").strip()[:80]
    selected_color_hex = _clean_color_hex(request.POST.get("selected_color_hex") or "")
    cart_line_key = (request.POST.get("cart_key") or "").strip()

    if quantity < 1:
        quantity = 1

    cart = _get_cart(request.session)
    key = cart_line_key if update and cart_line_key in cart else _cart_key(product.id, selected_color_name)
    old_entry = _cart_entry(cart.get(key, 0))

    if update:
        cart[key] = {
            "quantity": quantity,
            "selected_color_name": old_entry["selected_color_name"] or selected_color_name,
            "selected_color_hex": old_entry["selected_color_hex"] or selected_color_hex,
        }
    else:
        cart[key] = {
            "quantity": int(old_entry["quantity"]) + quantity,
            "selected_color_name": selected_color_name,
            "selected_color_hex": selected_color_hex,
        }

    request.session.modified = True
    return redirect("shop:cart_detail")


@require_GET
def cart_detail(request):
    items, total = _cart_summary(request.session)
    cart_lines = [
        {
            "id": line["product"].id,
            "title": line["product"].title,
            "quantity": line["quantity"],
            "price": str(line["product"].price),
            "lineTotal": str(line["line_total"]),
            "weightGrams": int(getattr(line["product"], "weight_grams", 200) or 200),
            "selectedColorName": line.get("selected_color_name", ""),
            "selectedColorHex": line.get("selected_color_hex", ""),
        }
        for line in items
    ]
    toast_messages = []
    for m in get_messages(request):
        toast_messages.append({"level": m.tags or "info", "text": str(m)})

    return render(
        request,
        "cart.html",
        {
            "cart_items": items,
            "cart_total": total,
            "cart_lines": cart_lines,
            "shipping_rules": shipping.client_payload(),
            "toast_messages": toast_messages,
            "shipping_debug": settings.DEBUG,
        },
    )


@require_POST
def cart_remove(request, product_id):
    cart = _get_cart(request.session)
    cart_key = (request.POST.get("cart_key") or "").strip()
    pid = cart_key if cart_key in cart else str(product_id)
    if pid in cart:
        del cart[pid]
        request.session.modified = True
    return redirect("shop:cart_detail")


@login_required
@require_POST
def order_create(request):
    items, subtotal = _cart_summary(request.session)
    if not items:
        return redirect("shop:cart_detail")

    country = (request.POST.get("shipping_country") or "").strip().upper()
    carrier = (request.POST.get("shipping_carrier") or "").strip().lower()
    if not country or not carrier:
        messages.error(request, "Please choose a country and shipping method.")
        return redirect("shop:cart_detail")

    tw = _cart_total_weight_grams(items)
    ship_amount, err = shipping.quote_shipping(country, carrier, tw, subtotal)
    if err:
        messages.error(request, err)
        return redirect("shop:cart_detail")

    grand_total = (subtotal + ship_amount).quantize(Decimal("0.01"))

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            total_amount=grand_total,
            shipping_cost=ship_amount,
            shipping_carrier=carrier,
            shipping_country_code=country,
            status=Order.STATUS_PROCESSING,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price_at_purchase=item["product"].price,
                selected_color_name=item.get("selected_color_name", ""),
                selected_color_hex=item.get("selected_color_hex", ""),
            )

    request.session["cart"] = {}
    request.session.modified = True

    try:
        session = _create_stripe_session_for_order(request, order)
    except Exception as e:
        print(str(e))
        return HttpResponse(str(e), status=500)

    return redirect(session.url, permanent=False)


@csrf_exempt
@login_required
@require_POST
def create_order_from_product(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    title = (payload.get("title") or "").strip()
    if not title:
        return JsonResponse({"error": "Product title is required."}, status=400)

    quantity = payload.get("quantity", 1)
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Quantity must be an integer."}, status=400)
    if quantity <= 0:
        return JsonResponse(
            {"error": "Quantity must be greater than zero."}, status=400
        )

    raw_price = payload.get("price")
    try:
        price = Decimal(str(raw_price)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        return JsonResponse({"error": "Price must be a valid number."}, status=400)
    if price <= 0:
        return JsonResponse({"error": "Price must be greater than zero."}, status=400)

    category = (
        payload.get("category") or Product.CATEGORY_SCENTED
    ).strip() or Product.CATEGORY_SCENTED
    allowed_categories = {value for value, _label in Product.CATEGORY_CHOICES}
    if category not in allowed_categories:
        category = Product.CATEGORY_SCENTED
    description = (
        payload.get("description") or "Product from storefront"
    ).strip() or "Product from storefront"
    selected_color_name = str(payload.get("selected_color_name") or "").strip()[:80]
    selected_color_hex = _clean_color_hex(str(payload.get("selected_color_hex") or ""))

    with transaction.atomic():
        product, _ = Product.objects.get_or_create(
            title=title,
            defaults={
                "description": description,
                "price": price,
                "category": category,
                "stock": 0,
                "image": payload.get("image") or "products/placeholder.jpg",
            },
        )

        price_at_purchase = product.price
        total_amount = (price_at_purchase * quantity).quantize(Decimal("0.01"))
        order = Order.objects.create(
            user=request.user, total_amount=total_amount, status=Order.STATUS_PROCESSING
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_purchase=price_at_purchase,
            selected_color_name=selected_color_name,
            selected_color_hex=selected_color_hex,
        )

    return JsonResponse(
        {
            "status": "ok",
            "order_id": order.id,
            "product": product.title,
            "quantity": quantity,
            "total_amount": str(order.total_amount),
        },
        status=201,
    )


@login_required
@require_POST
def create_checkout_session(request):
    items, subtotal = _cart_summary(request.session)
    if not items:
        return redirect("shop:cart_detail")

    country = (request.POST.get("shipping_country") or "").strip().upper()
    carrier = (request.POST.get("shipping_carrier") or "").strip().lower()
    if not country or not carrier:
        messages.error(request, "Please choose a country and shipping method.")
        return redirect("shop:cart_detail")

    tw = _cart_total_weight_grams(items)
    ship_amount, err = shipping.quote_shipping(country, carrier, tw, subtotal)
    if err:
        messages.error(request, err)
        return redirect("shop:cart_detail")

    grand_total = (subtotal + ship_amount).quantize(Decimal("0.01"))

    # Create the order in DB first so we have an order_id for Stripe metadata.
    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            total_amount=grand_total,
            shipping_cost=ship_amount,
            shipping_carrier=carrier,
            shipping_country_code=country,
            status=Order.STATUS_PROCESSING,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price_at_purchase=item["product"].price,
                selected_color_name=item.get("selected_color_name", ""),
                selected_color_hex=item.get("selected_color_hex", ""),
            )

    # Create Stripe session outside the DB transaction to avoid holding the
    # connection open during a network call.
    try:
        stripe_session = _create_stripe_session_for_order(request, order)
    except stripe.error.StripeError as e:
        order.delete()
        import logging

        logging.getLogger(__name__).error(
            "Stripe error for user %s: %s", request.user, e
        )
        messages.error(
            request,
            f"Erreur de paiement: {e.user_message or 'Stripe indisponible. Réessayez dans quelques instants.'}",
        )
        return redirect("shop:cart_detail")
    except Exception:
        order.delete()
        import logging

        logging.getLogger(__name__).exception(
            "Checkout error for user %s", request.user
        )
        messages.error(
            request,
            "Une erreur inattendue s'est produite lors du paiement. Veuillez réessayer.",
        )
        return redirect("shop:cart_detail")

    # Save cart snapshot so it can be restored if user cancels payment.
    request.session["_pre_checkout_cart"] = dict(request.session.get("cart", {}))
    request.session["_pre_checkout_order_id"] = str(order.id)
    request.session["cart"] = {}
    request.session.modified = True
    return redirect(stripe_session.url, permanent=False)


@login_required
@require_POST
def create_checkout_session_for_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == Order.STATUS_PAID:
        return redirect("shop:payment_success")

    try:
        session = _create_stripe_session_for_order(request, order)
    except Exception as e:
        print(str(e))
        return HttpResponse(str(e), status=500)

    return redirect(session.url, permanent=False)


@require_GET
def payment_success(request):
    return render(request, "payment_success.html")


@require_GET
def payment_cancel(request):
    return render(request, "payment_cancel.html")


@require_GET
def checkout_success(request):
    session_id = request.GET.get("session_id", "")
    payment_verified = _mark_order_paid_from_checkout_session(session_id)
    return render(request, "success.html", {"payment_verified": payment_verified})


@require_GET
def checkout_cancel(request):
    # Restore cart if user came from checkout and cancelled
    saved_cart = request.session.pop("_pre_checkout_cart", None)
    if saved_cart:
        request.session["cart"] = saved_cart
        request.session.modified = True
    request.session.pop("_pre_checkout_order_id", None)
    return render(request, "cancel.html")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    if not settings.STRIPE_WEBHOOK_SECRET:
        return JsonResponse(
            {"error": "Stripe webhook secret is not configured."}, status=500
        )

    try:
        stripe.api_key = _get_validated_stripe_secret_key()
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=500)
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return JsonResponse({"error": "Invalid webhook payload."}, status=400)

    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        payment_status = session_data.get("payment_status")
        if payment_status and payment_status != "paid":
            return JsonResponse(
                {"status": "ignored", "reason": "payment not completed"}
            )

        metadata = session_data.get("metadata", {})
        order_id = metadata.get("order_id") or session_data.get("client_reference_id")

        if order_id:
            try:
                order = Order.objects.get(id=order_id)

                final_amount = _amount_total_to_decimal(session_data)
                updated_fields = []
                if final_amount is not None and order.total_amount != final_amount:
                    order.total_amount = final_amount
                    updated_fields.append("total_amount")

                was_already_paid = order.status == Order.STATUS_PAID
                order.status = Order.STATUS_PAID
                updated_fields.append("status")

                shipping_details = session_data.get("shipping_details") or {}
                address_data = shipping_details.get("address") or {}
                if address_data:
                    try:
                        order.shipping_address = address_data.get("line1", "")
                        order.city = address_data.get("city", "")
                        order.postal_code = address_data.get("postal_code", "")
                        order.country = address_data.get("country", "")
                        updated_fields.extend(
                            ["shipping_address", "city", "postal_code", "country"]
                        )
                    except Exception as e:
                        print(f"Webhook shipping save failed for order {order.id}: {e}")

                if updated_fields:
                    order.save(update_fields=sorted(set(updated_fields)))
                    if "status" in updated_fields and not was_already_paid:
                        _decrement_stock_for_order(order.id)
                        send_order_confirmation_email(order)
                        send_admin_order_notification(order)
            except Order.DoesNotExist:
                return JsonResponse({"error": "Order not found."}, status=404)

    return JsonResponse({"status": "ok"})


@require_POST
def subscribe_newsletter(request):
    """Handle newsletter subscription via AJAX."""
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()

        if not email:
            return JsonResponse(
                {"success": False, "error": "Email is required."}, status=400
            )

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse(
                {"success": False, "error": "Please enter a valid email address."},
                status=400,
            )

        if NewsletterUser.objects.filter(email__iexact=email).exists():
            return JsonResponse(
                {"success": False, "error": "Email already subscribed"}, status=400
            )

        try:
            NewsletterUser.objects.create(email=email)
        except IntegrityError:
            return JsonResponse(
                {"success": False, "error": "Email already subscribed"}, status=400
            )

        return JsonResponse(
            {"success": True, "message": "Thank you for joining our journey!"}
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=500)


@staff_member_required
@require_POST
def ai_enhance_description(request):
    try:
        body = json.loads(request.body)
        prompt = body.get("prompt", "").strip()
        if not prompt:
            return JsonResponse({"error": "Prompt is required."}, status=400)

        history = sanitize_history(body.get("history"))
        on_product_form = bool(body.get("on_product_form"))
        fill_form = body.get("fill_product_form")
        if fill_form is None:
            fill_form = wants_product_form_fill(prompt, on_product_form=on_product_form)

        if fill_form:
            result = generate_product_form_fields(prompt, history=history)
            return JsonResponse(
                {
                    "mode": "form_fill",
                    "form_fields": result["form_fields"],
                    "message": result["message"],
                },
                json_dumps_params={"ensure_ascii": False},
            )

        admin_context = _build_admin_copilot_context(prompt)
        prompt_with_admin_context = (
            f"{admin_context}\n\n"
            "<admin_page_and_user_request>\n"
            f"{prompt}\n"
            "</admin_page_and_user_request>"
        )

        use_stream = body.get("stream", True)
        if use_stream:
            response = StreamingHttpResponse(
                stream_sse_events(prompt_with_admin_context, history=history),
                content_type="text/event-stream; charset=utf-8",
            )
            response["Cache-Control"] = "no-cache"
            response["X-Accel-Buffering"] = "no"
            return response

        enhanced = generate_chat_reply(prompt_with_admin_context, history=history)
        return JsonResponse(
            {"enhanced_description": enhanced},
            json_dumps_params={"ensure_ascii": False},
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


@staff_member_required
@require_POST
def copilot_admin_action(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    action = (body.get("action") or "").strip()
    params = body.get("params") or {}
    if not isinstance(params, dict):
        return JsonResponse(
            {"success": False, "error": "Action params must be an object."},
            status=400,
        )

    try:
        if action == "update_order_status":
            order_id = int(params.get("order_id"))
            status = (params.get("status") or "").strip()
            allowed_statuses = {value for value, _label in Order.STATUS_CHOICES}
            if status not in allowed_statuses:
                return JsonResponse(
                    {"success": False, "error": "Unsupported order status."},
                    status=400,
                )
            order = get_object_or_404(Order, id=order_id)
            old_status = order.status
            order.status = status
            order.save(update_fields=["status"])
            email_sent = send_order_status_update_email(order, old_status=old_status)
            return JsonResponse(
                {
                    "success": True,
                    "message": (
                        f"Order #{order.id}: status changed from {old_status} to {status}. "
                        + (
                            "Customer email notification sent."
                            if email_sent
                            else "Customer email notification skipped (email not configured or customer email missing)."
                        )
                    ),
                    "url": f"/admin/shop/order/{order.id}/change/",
                }
            )

        if action == "update_order_tracking":
            order_id = int(params.get("order_id"))
            tracking_number = (params.get("tracking_number") or "").strip()[:120]
            tracking_url = (params.get("tracking_url") or "").strip()[:500]
            if tracking_url:
                if not tracking_url.startswith(("http://", "https://")):
                    return JsonResponse(
                        {"success": False, "error": "Tracking URL must start with http:// or https://."},
                        status=400,
                    )
            order = get_object_or_404(Order, id=order_id)
            order.tracking_number = tracking_number
            order.tracking_url = tracking_url
            order.save(update_fields=["tracking_number", "tracking_url"])
            email_sent = send_order_status_update_email(order, old_status=order.status)
            return JsonResponse(
                {
                    "success": True,
                    "message": (
                        f"Tracking updated for order #{order.id}. "
                        + (
                            "Customer email notification sent."
                            if email_sent
                            else "Customer email notification skipped (email not configured or customer email missing)."
                        )
                    ),
                    "url": f"/admin/shop/order/{order.id}/change/",
                }
            )

        if action == "update_order_note":
            order_id = int(params.get("order_id"))
            admin_note = (params.get("admin_note") or "").strip()[:2000]
            order = get_object_or_404(Order, id=order_id)
            order.admin_note = admin_note
            order.save(update_fields=["admin_note"])
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Internal note saved for order #{order.id}.",
                    "url": f"/admin/shop/order/{order.id}/change/",
                }
            )

        if action == "update_product_stock":
            product_id = int(params.get("product_id"))
            stock = int(params.get("stock"))
            if stock < 0:
                return JsonResponse(
                    {"success": False, "error": "Stock cannot be negative."},
                    status=400,
                )
            product = get_object_or_404(Product, id=product_id)
            old_stock = product.stock
            product.stock = stock
            product.save(update_fields=["stock"])
            return JsonResponse(
                {
                    "success": True,
                    "message": f"{product.title}: stock changed from {old_stock} to {stock}.",
                    "url": f"/admin/shop/product/{product.id}/change/",
                }
            )

        if action == "adjust_product_stock":
            product_id = int(params.get("product_id"))
            delta = int(params.get("delta"))
            product = get_object_or_404(Product, id=product_id)
            old_stock = product.stock
            new_stock = old_stock + delta
            if new_stock < 0:
                return JsonResponse(
                    {"success": False, "error": "Stock cannot become negative."},
                    status=400,
                )
            product.stock = new_stock
            product.save(update_fields=["stock"])
            return JsonResponse(
                {
                    "success": True,
                    "message": f"{product.title}: stock changed from {old_stock} to {new_stock}.",
                    "url": f"/admin/shop/product/{product.id}/change/",
                }
            )

        if action == "update_product_price":
            product_id = int(params.get("product_id"))
            price = Decimal(str(params.get("price"))).quantize(Decimal("0.01"))
            if price < 0:
                return JsonResponse(
                    {"success": False, "error": "Price cannot be negative."},
                    status=400,
                )
            product = get_object_or_404(Product, id=product_id)
            old_price = product.price
            product.price = price
            product.save(update_fields=["price"])
            return JsonResponse(
                {
                    "success": True,
                    "message": f"{product.title}: price changed from {_format_money(old_price)} to {_format_money(price)}.",
                    "url": f"/admin/shop/product/{product.id}/change/",
                }
            )

        if action == "create_newsletter_subscriber":
            email = (params.get("email") or "").strip().lower()
            validate_email(email)
            subscriber, created = NewsletterUser.objects.get_or_create(email=email)
            return JsonResponse(
                {
                    "success": True,
                    "message": (
                        f"{subscriber.email} added to newsletter."
                        if created
                        else f"{subscriber.email} is already subscribed."
                    ),
                    "url": "/admin/shop/newsletteruser/",
                }
            )

    except (TypeError, ValueError, InvalidOperation, ValidationError):
        return JsonResponse(
            {"success": False, "error": "Invalid action parameters."},
            status=400,
        )

    return JsonResponse(
        {"success": False, "error": "Unsupported action."},
        status=400,
    )

"""
Email utilities for MIMOSA Atelier order notifications.
Uses Django's built-in email backend (configured for SendGrid SMTP).
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

STATUS_LABELS = {
    "processing": "In preparation",
    "paid": "Payment confirmed",
    "shipped": "Shipped",
    "delivered": "Delivered",
    "canceled": "Cancelled",
}


def _email_configured() -> bool:
    """Return True only if SMTP credentials are set."""
    return bool(getattr(settings, "EMAIL_HOST_PASSWORD", ""))


def send_order_confirmation_email(order) -> bool:
    """
    Send a branded order confirmation email to the customer.
    Safe to call multiple times — silently skips if email not configured
    or user has no email address.
    """
    if not _email_configured():
        logger.info(
            "Email not configured — skipping order confirmation for order #%s.",
            order.id,
        )
        return False

    customer_email = getattr(order.user, "email", "") or ""
    if not customer_email:
        logger.warning(
            "Order #%s: user has no email — skipping confirmation.", order.id
        )
        return False

    try:
        items = list(order.items.select_related("product").all())
        context = {
            "order": order,
            "items": items,
            "site_url": settings.SITE_URL,
            "customer_name": order.user.get_full_name() or order.user.username,
        }

        html_body = render_to_string("emails/order_confirmation.html", context)
        text_body = render_to_string("emails/order_confirmation.txt", context)

        msg = EmailMultiAlternatives(
            subject=f"MIMOSA Atelier — Your order #{order.id} is confirmed ✨",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer_email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info(
            "Order confirmation email sent for order #%s to %s.",
            order.id,
            customer_email,
        )
        return True
    except Exception as exc:
        logger.error(
            "Failed to send order confirmation for order #%s: %s", order.id, exc
        )
        return False


def send_admin_order_notification(order) -> bool:
    """
    Send a new-order notification to the store admin.
    Uses ADMIN_ORDER_EMAIL setting — silently skips if not set.
    """
    admin_email = getattr(settings, "ADMIN_ORDER_EMAIL", "")
    if not admin_email or not _email_configured():
        return False


def send_order_status_update_email(order, *, old_status: str = "") -> bool:
    """Notify the customer when staff changes the order status."""
    if not _email_configured():
        logger.info(
            "Email not configured — skipping status update for order #%s.", order.id
        )
        return False

    customer_email = getattr(order.user, "email", "") or ""
    if not customer_email:
        logger.warning("Order #%s: user has no email — skipping status update.", order.id)
        return False

    try:
        context = {
            "order": order,
            "site_url": settings.SITE_URL,
            "customer_name": order.user.get_full_name() or order.user.username,
            "old_status": old_status,
            "old_status_label": STATUS_LABELS.get(old_status, old_status),
            "status_label": STATUS_LABELS.get(order.status, order.get_status_display()),
        }
        html_body = render_to_string("emails/order_status_update.html", context)
        text_body = render_to_string("emails/order_status_update.txt", context)

        msg = EmailMultiAlternatives(
            subject=f"MIMOSA Atelier — Order #{order.id}: {context['status_label']}",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer_email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info("Order status update email sent for order #%s.", order.id)
        return True
    except Exception as exc:
        logger.error("Failed to send status update for order #%s: %s", order.id, exc)
        return False

    try:
        items = list(order.items.select_related("product").all())
        context = {
            "order": order,
            "items": items,
            "site_url": settings.SITE_URL,
        }

        html_body = render_to_string("emails/order_notification_admin.html", context)

        msg = EmailMultiAlternatives(
            subject=f"[MIMOSA] New paid order #{order.id} — {order.user.username}",
            body=(
                f"New paid order #{order.id}.\n"
                f"Customer: {order.user.username} <{order.user.email}>\n"
                f"Total: {order.total_amount} EUR\n"
                f"{settings.SITE_URL}/admin/shop/order/{order.id}/change/"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info("Admin notification sent for order #%s.", order.id)
        return True
    except Exception as exc:
        logger.error(
            "Failed to send admin notification for order #%s: %s", order.id, exc
        )
        return False

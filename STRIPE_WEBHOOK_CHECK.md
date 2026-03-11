# Stripe Webhook Production Check

This guide verifies that Stripe payment events reach Django and update order status correctly.

## 1. Required Environment Variables

Set these in Render:

- `STRIPE_PUBLIC_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `DEBUG=False`

Endpoint used by project:

- `/payments/webhook/stripe/`

## 2. Endpoint URL on Production

Example:

```bash
https://mimosa-atelier.onrender.com/payments/webhook/stripe/
```

## 3. Quick Health Check

Send a simple POST (without Stripe signature). Expected response is an error about invalid payload/signature, which proves endpoint is reachable.

```bash
curl -i -X POST "https://mimosa-atelier.onrender.com/payments/webhook/stripe/" \
  -H "Content-Type: application/json" \
  -d '{"ping":true}'
```

Expected:

- HTTP `400` with JSON error (`Invalid webhook payload.`)

## 4. Full Real Check with Stripe CLI (Recommended)

Install Stripe CLI and login:

```bash
stripe login
```

Forward Stripe events to your production endpoint:

```bash
stripe listen --events checkout.session.completed \
  --forward-to https://mimosa-atelier.onrender.com/payments/webhook/stripe/
```

Stripe CLI prints a signing secret like `whsec_...`.
Copy it into Render as:

- `STRIPE_WEBHOOK_SECRET=whsec_...`

Restart service after updating env vars.

Trigger a test event:

```bash
stripe trigger checkout.session.completed
```

Expected result:

- webhook endpoint responds with HTTP `200`
- Django updates matching `Order.status` to `paid`

## 5. Verify Order Sync in Django

Open admin:

```bash
https://mimosa-atelier.onrender.com/admin/
```

Check `Order` record:

- before event: `processing`
- after successful webhook or success fallback: `paid`

## 6. End-to-End Checkout Test

1. Log in as user on site.
2. Add product to cart.
3. Click `Place order`.
4. Complete payment in Stripe Checkout.
5. Return to `/success/?session_id=...`.
6. Open profile page and verify order status is `paid`.

## 7. Troubleshooting

If status stays `processing`:

- Check Render logs for `/payments/webhook/stripe/` requests.
- Verify `STRIPE_WEBHOOK_SECRET` exactly matches Stripe CLI/dashboard secret.
- Verify `STRIPE_SECRET_KEY` is valid and from same Stripe account.
- Confirm checkout session metadata includes `order_id`.
- Ensure HTTPS endpoint is public and not blocked.

## 8. Security Notes

- Never commit real Stripe keys to git.
- Rotate keys immediately if they were exposed.
- Keep webhook secret only in environment variables.

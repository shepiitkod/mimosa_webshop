# Frontend performance & motion guide

Reference for Mimosa storefront polish (June 2026). Keep new work aligned with these rules.

## Script load order

All storefront pages should end with:

```django
{% include 'includes/site_scripts.html' %}
```

Load order (all `defer`):

1. `translations.js` — locale strings; init on `DOMContentLoaded`
2. `animations.js` — scroll reveals + image fade-in (skip on auth pages via `site_scripts_animations=False`)
3. `kinetic-header.js` — sticky dock header, mobile menu, `--kinetic-scroll`
4. `site-ui.js` — back-to-top, FAB hide-on-scroll, menu focus trap

Optional page scripts: pass `site_scripts_extra` list to the include.

**Do not** add blocking `<script src="translations.js">` without `defer`.

## Motion tokens (`static/styles.css`)

| Token | Value | Use |
|-------|-------|-----|
| `--motion-fast` | 180ms | `:active`, hovers |
| `--motion-base` | 320ms | cards, FAB, header |
| `--motion-slow` | 480ms | page fade, dock bar |
| `--ease-out` | `cubic-bezier(0.22, 1, 0.36, 1)` | entrances, lifts |
| `--ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | toggles |

Avoid bounce easing. Respect `@media (prefers-reduced-motion: reduce)`.

## Breakpoints

| Tier | Query |
|------|--------|
| Mobile | `max-width: 767px` |
| Tablet | `768px – 1023px` |
| Desktop | `min-width: 1024px` |

Mobile menu + header auto-hide: **767px only**. Tablet uses compact layout rules at **1023px**.

## Images

### Static assets

Use `templates/includes/picture_opt.html` for `assets/images/*` (WebP + fallback).

### Product uploads

- `shop/image_utils.py` generates `{stem}_400.webp`, `_800`, `_1200` on `Product` save.
- Templates: `{% load product_media %}` + `{% product_picture product.image ... %}`.
- Hero marquee: full track desktop, `hero_marquee_set_lite.html` (8 images) on mobile via `.hero-bg-track--lite`.

### LCP hints

- Hero foreground: `fetchpriority="high"` on first 2–3 images.
- Product detail main image: `loading="eager"` + `fetchpriority="high"`.
- Thumbnails / below fold: `loading="lazy"`.

### Placeholders

`.product-framed-image` starts at `opacity: 0` with `#ebe6dc` background; `animations.js` adds `.is-loaded` on `load`.

## Header behaviour

Classes toggled by `kinetic-header.js`:

- `site-header--at-top` — scrollY &lt; 40
- `site-header--dock` — frosted compact bar
- `site-header--hidden` — mobile auto-hide on fast scroll down

CSS: `position: sticky; top: 0`.

## Content visibility

Below-fold sections use `content-visibility: auto` (portfolio, footer, related products, newsletter).

## Verification checklist

Run Lighthouse (mobile + desktop) on `/`, `/products/`, a product detail URL, `/cart/`.

Manual QA:

- [ ] Language switch + cart on all breakpoints
- [ ] Mobile menu open/close + focus trap
- [ ] `prefers-reduced-motion: reduce` — no marquee/float/reveals
- [ ] Stripe checkout unchanged
- [ ] Admin order list hover + copilot typing indicator

## Admin

- Order cards: `static/admin_custom_v2.css`
- Copilot: `static/admin_copilot.css` + `admin_copilot.js`
- Both respect `prefers-reduced-motion`

# MIMOSA Atelier — design notes (site-redesign)

What changed, and why. The brand idea that drives every decision:
**light and flame** — a dark, warm room where a candle is lit, then the ivory
calm of an atelier in Nîmes.

---

## 1. Principles

| Decision | Why |
| --- | --- |
| Ivory paper `#f8f4ed`, ink `#1d1a16`, one warm accent (flame `#f0a64a`, gold `#a98443`) | Luxury houses (Diptyque, Trudon, Le Labo) use very few colours; the products are pastel, so the frame must stay quiet. |
| Cormorant Garamond 300 for display (roman + italic), DM Sans for UI | Editorial contrast: hairline serif for emotion, clean sans for prices and buttons. The italic carries the "voice" (`L’art de la *bougie*`). |
| Uppercase, wide-tracked micro-labels | Reads as "maison", gives hierarchy without bold weights. |
| Pill buttons, ink filled → outline on hover | One button family everywhere (`.btn`, `.btn--ghost`, `.btn--light`). |
| Radii 4 / 10 / 18 px, one soft and one lifted shadow | Calm, consistent cards; no heavy drop shadows. |
| Lots of air, `--section-y: clamp(72px, 10vw, 140px)` | Space is the most premium material. |
| French as the brand voice | New copy is written in French first; EN/UA/RU translate it. Ribbons stay French in every language on purpose. |

All tokens live in `static/atelier.css` (`:root`). Layout per page lives in
`static/site.css`; the homepage intro in `static/intro.css`.

## 2. The intro ("vau" block)

- **Dark warm room, a live flame.** The flame is a ~60-line WebGL fragment
  shader (`static/intro.js`): fbm noise body, blue root, warm glow and a heat
  haze that shimmers above it. It **leans when the cursor sweeps past**, like
  a candle in a draught — a small, honest piece of physics that makes the page
  feel alive.
- **11 atelier photos in CSS 3D space** at different depths. On the first visit
  of the session they drift in from the depth (≤ 2 s) while a ring of light
  runs outward from the flame. Repeat visits in the same session skip it
  (`sessionStorage`, decided in `<head>` so there is no flash).
- **Headline visible from the first paint** (it is the LCP). It only settles
  by a few pixels (transform). It is translated by a tiny inline script before
  paint, so it never changes after load.
- **Parallax**: mouse turns the whole scene (perspective does the depth work);
  phones get a slow drift or device tilt (Android, no permission prompt).
- **Scroll**: the section pins; the camera flies through the photos, the last
  one fills the screen and dissolves into ivory, flowing into the next block.
- **Fallbacks**: no WebGL, weak device (`deviceMemory < 4`, `saveData`),
  software GL (SwiftShader/llvmpipe) or a dropping frame rate → CSS flame.
  `prefers-reduced-motion` or no JS → one still, lit composition.
- **No libraries**: GSAP/three.js/Lenis would have cost 40–150 KB and a CDN
  request for effects that are ~400 lines of vanilla code. The CDNs are not
  reachable from the build sandbox either, so nothing could have been verified.

## 3. Structure

**Header** — Boutique (mega menu: collections + occasions + two editorial
cards), Sur mesure, L’atelier · centred logo · language, account, bag with
count. Transparent with an ivory logo over the intro, solid elsewhere, hides
on scroll down and returns on scroll up. Phone: burger + drawer.
The logo was re-cut from the JPEG into transparent ink and ivory PNGs.

**Homepage**, in order: intro → *Pour quelle occasion ?* (4 occasions → the
Boutique filtered) → *Nouveautés* (8 newest products, hover shows the second
photo and *Ajouter au panier*) → *Fait main à Nîmes* (4 gestures swap on
scroll) → *Sur mesure* → reviews (only published ones; hidden when none) +
Instagram-style grid (atelier photos linking to the account — they are not
pulled from Instagram) → compact Seconde vie band → newsletter with the
−10 % welcome code → footer. The "Welcome to MIMOSA" paragraph is gone; the
gestures block tells that story better.

**Boutique** (`/boutique/`, `/boutique/<collection>/`) — one template for
every collection, with a tinted collection header, collection chips and
filters (occasion, price band, sort). Filters apply on change (button kept for
no-JS). The old Plaster Sachets landing text lives on as a "story" section
under the sachets collection.

**Occasions** (`shop/catalog.py`) — each occasion maps to categories by
default; staff can tick occasions per product in the admin to override.
No new table needed.

**Product page** — gallery of all photos (thumbnails, swipe on phones),
hover zoom on desktop, full-screen lightbox; buy box with colour, quantity
stepper, *Expédié sous 48 h · Livraison offerte dès 85 €*; accordions
(composition, burn time, care, delivery & returns — empty ones are hidden);
reviews; related products; a sticky *Ajouter au panier* bar on phones.

**Sur mesure** (`/sur-mesure/`) — three kinds of commissions, three steps,
and a request form (occasion, date, quantity, wishes, reference photo).
Requests are stored in `CustomOrderRequest` (admin, with status) and mailed
to `ADMIN_ORDER_EMAIL` through the existing SMTP/SendGrid settings. Spam
honeypot, 8 MB image limit, past dates refused. The consultation button and
both intro CTAs lead here.

**L’atelier** (replaces About, 301 from `/about/`), **FAQ & entretien**
(new), **Contact** (emoji replaced by line icons), cart, payment, login and
register restyled with the same tokens.

## 4. Old addresses (301) and SEO

| Old | New |
| --- | --- |
| `/products/` | `/boutique/` |
| `/products/category/<slug>/` | `/boutique/<slug>/` (query kept) |
| `/products/bento/` | `/boutique/bento-candles/` |
| `/products/plaster-sachets/` | `/boutique/plaster-sachets/` |
| `/products/rose/`, `/products/decorative-candles/` | `/boutique/decorative-candles/` |
| `/about/` | `/atelier/` |

Product pages keep `/products/<id>/<slug>/`. The sitemap lists the new pages
and every collection. Canonical URLs are absolute.

## 5. Performance

- Fonts self-hosted (`static/fonts`, unicode-range subsets incl. Cyrillic),
  3 preloads, no render-blocking Google CSS.
- Atelier photos: 480/960 px AVIF + WebP (`static/assets/images/r/`,
  `.../intro/`), lazy below the fold, explicit sizes.
- Product photos: Cloudinary `f_auto,q_auto,w_400/800/1200` srcset; main
  product photo preloaded.
- Only transform / opacity / canvas are animated.
- Lighthouse (local, mobile profile, brotli like Vercel):
  home 91, boutique 89, product 90, sur mesure 91; accessibility 100.
  Desktop home 97.

## 6. Accessibility

Skip link, visible focus ring (flame colour), keyboard mega menu (Enter opens,
Escape closes), focus-trapped drawer, `alt` on content photos (decorative ones
empty), contrast ≥ 4.5:1 for text (muted grey and small gold were darkened),
reduced-motion support everywhere.

## 7. Things the owner should do

1. **Stripe promotion code** — in Stripe → Products → Coupons create a −10 %
   coupon, then a promotion code `BIENVENUE10` on it ("First-time order
   only"). Checkout already accepts promotion codes; until the code exists the
   newsletter shows a code that Stripe will refuse.
   The code can be changed with the `NEWSLETTER_WELCOME_CODE` env variable.
2. **Reviews** — add real reviews in Admin → Reviews and tick *Published*.
3. **Occasions** — optionally tick occasions on products in the admin.
4. **Check the policy copy** in the FAQ (14-day returns, damaged parcels,
   48 h dispatch) against your actual terms.
5. **Previews** of this branch run on a demo database with demo products
   (`DEMO_PREVIEW` in settings, `shop/demo.py`). Production is unaffected;
   the migration runs on the real database at deploy, as before.

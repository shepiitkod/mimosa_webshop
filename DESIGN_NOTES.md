# MIMOSA Atelier — design notes (site-redesign)

What changed, and why. The brand idea that drives every decision:
**an atelier, not a render** — the ivory calm of a workshop in Nîmes, real
photographs of real pieces, printed-page typography. Nothing on the site
should look generated (no glows, flames, particles or gradients).

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
`static/site.css`; the homepage first block in `static/hero.css`.

## 2. The first block (rebuilt — "made by a studio, not by an AI")

**Removed**, because nothing on the page should be invented: the WebGL and CSS
flames, every glow and halo, the heat haze, the light dot at the bottom, the
warm light that followed the cursor, the photos scattered at angles on a dark
background, the gold-gradient italic headline, the "scroll" line and the dark
"room". The brand is light, pastel and mimosa-yellow, so the hero now is too.
Glows were also removed from product cards, list dots, the newsletter and the
login page; headline italics are ink, not gold.

**Now** — *le lookbook*, built only from the atelier's real photographs and
type (the owner chose this one of the two variants reviewed; the other, a
slow slideshow, was removed). The block holds while you scroll and each
plate is uncovered from the right over the previous one, like turning a
page; folio number, caption with the product's name and price from the
database (linked to it) and a column of plate numbers you can click.

How it stays smooth (it lagged at first):

- scrolling is always native. A home-made "smooth wheel" script that
  intercepted the mouse wheel was removed: it made the page trail far
  behind the wheel (≈ 0.7 s to settle, now ≈ 15 ms);
- the page turn moves the plate and its photo in opposite directions with
  `transform` only (no animated `clip-path`), so the photos are never
  repainted while scrolling; the section is measured once, not every frame;
- the frame no longer resizes when the header hides;
- the header writes its CSS variables only when they change (a variable on
  `<html>` restyles the whole page); the parallax reads all positions
  before writing;
- the next plates load after the page has loaded, never before the first.

Both carry the brand's own line from its printed card, *«Faire briller la
bougie pour que le vœu se réalise»*, set in a handwriting face (Allura,
self-hosted), plain words (what it is, where it is made) and the two ways in:
Boutique and Sur mesure. If `static/assets/video/hero.mp4` (and
`hero-poster.jpg`) exist, the plate plays that film instead of the photos.

## 2b. Seconde vie — the fragrance table

**Removed**: the horizontal ribbon of fragrance cards and its glass modal
(data hard-coded in JavaScript, English only, the first card washed out by a
fade, big empty gaps around it, invisible to Google and without JS).

**Now**: a printed-catalogue table of the 18 fragrances, the way an atelier
lists its scents: small photo, name, family, notes, intensity 1–5 as five
short bars, seasons, moments, "se marie avec". Clicking a row opens it in
place: larger photo, description and mood. Filters for family, intensity
(légère 1–2 · moyenne 3 · intense 4–5) and season, sorting by name or
intensity. On phones each fragrance is a card that opens; the filters sit in
a 2 × 2 grid; nothing scrolls sideways.

- Data lives in the `Fragrance` model (Admin → Fragrances: text, notes,
  intensity, seasons, moments, translations, an optional photo that replaces
  the default one, order, active). Migration `0023_fragrance_data` fills it.
- The table is rendered by Django (`shop/fragrances.py`,
  `includes/fragrance_table.html`), so it is complete without JavaScript and
  for search engines; the filters are a plain GET form (`?famille=floral&
  saison=ete&tri=intensite-desc`) that also works without JS.
  `fragrance_catalog.js` only filters/sorts in place (keeping the URL
  shareable) and opens rows. `#parfum-mimosa` opens that fragrance.
- Names and notes stay in French in every language (they are the product's
  names). Families, seasons, moments and the interface are translated through
  `translations.js` (`frag-t-*`, `frag-season-*`, `ft-*`); description and
  mood through `Fragrance.i18n`.
- Lighthouse mobile on `/seconde-vie/`: performance 92, accessibility 100.

## 3. Structure

**Header** — Boutique (mega menu: collections + occasions + two editorial
cards), Sur mesure, L’atelier · centred logo · language, account, bag with
count. Solid ivory everywhere, hides on scroll down and returns on scroll up. Phone: burger + drawer.
The logo was re-cut from the JPEG into transparent ink and ivory PNGs.

**Homepage**, in order: first block (see 2) → *Pour quelle occasion ?* (4 occasions → the
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
- Atelier photos: 480/960 px AVIF + WebP (`static/assets/images/r/`), lazy below the fold, explicit sizes.
- Product photos: Cloudinary `f_auto,q_auto,w_400/800/1200` srcset; main
  product photo preloaded.
- Only transform / opacity / clip-path are animated.
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

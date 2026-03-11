<div align="center">

# 🕯️ Mimosa Atelier - Artisan Scented Candles

```
    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
    .                                                                   .
    .             (  )               (  )               (  )            .
    .            ( :: )             ( :: )             ( :: )           .
    .             \__/               \__/               \__/            .
    .              ||                 ||                 ||              .
    .           .-====-.           .-====-.           .-====-.          .
    .         .'  __    '.       .'  __    '.       .'  __    '.        .
    .        /   /  \     \     /   /  \     \     /   /  \     \       .
    .       |   | () |     |   |   | () |     |   |   | () |     |      .
    .       |   |____|     |   |   |____|     |   |   |____|     |      .
    .       |    ____    __|   |    ____    __|   |    ____    __|      .
    .       |   / __ \  /_/    |   / __ \  /_/    |   / __ \  /_/       .
    .       |  /_/  \_\_/      |  /_/  \_\_/      |  /_/  \_\_/         .
    .       |      __          |      __          |      __             .
    .       |_____/ /_____     |_____/ /_____     |_____/ /_____        .
    .      /______/_______/   /______/_______/   /______/_______/       .
    .                                                                   .
    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
```

✨ 🌿 Handcrafted elegance with a French soul.

</div>

## About

Mimosa Atelier is a boutique candle brand focused on aesthetic, handcrafted pieces designed to elevate everyday rituals. Inspired by French charm, each candle combines refined design, natural ingredients, and warm fragrance compositions for a premium sensory experience.

## Features

• 🌿 Multilingual interface: FR / EN / UA / RU  
• ✨ Newsletter subscription flow  
• 🕯️ PostgreSQL-powered data storage  
• 💳 Stripe Checkout with webhook-based payment sync  
• 🌿 Responsive design for desktop, tablet, and mobile

## Tech Stack

| Layer | Technology |
| --- | --- |
| Framework | Django 6.0 |
| Database | PostgreSQL |
| Hosting | Render |
| UI | Bootstrap + Custom CSS |

## Installation

```bash
git clone https://github.com/<your-username>/mimosa_webshop.git
cd mimosa_webshop
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Environment Variables

• `DATABASE_URL`  
• `DJANGO_SECRET_KEY`  
• `STRIPE_PUBLIC_KEY`  
• `STRIPE_SECRET_KEY`  
• `STRIPE_WEBHOOK_SECRET`

## Roadmap

- [x] Core storefront and catalog pages
- [x] Multilingual content support (FR/EN/UA/RU)
- [x] Newsletter subscription
- [x] PostgreSQL integration and production deployment
- [x] Stripe payments integration (Checkout + webhook + success fallback)
- [x] Full checkout workflow enhancements
- [ ] Order tracking dashboard

Made with ✨ for the Mimosa startup

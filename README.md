# mimosa_webshop
🕯 Mimosa — Atelier Artisanal Website
-----

First version of the official website for Mimosa Atelier Artisanal, a handcrafted decorative candle brand focused on aesthetics, softness, and premium presentation.

This project represents a clean and minimal product showcase built to reflect the brand’s identity — light, elegant, and modern.
-----

✨ About the Project

The website is designed as a visual-first landing page with a strong focus on:

Soft color palette and premium feel

Product-centered layout

Minimalist navigation

Multi-language interface (EN / FR / UA)

Clean and structured front-end architecture

The goal of this version is to establish an online presence and create a strong visual foundation for future e-commerce expansion.
-----

🛠 Tech Stack

HTML5

CSS3

Responsive Layout

Vanilla JavaScript (if applicable)
----
🎯 Version 1 Goals

Present the brand identity

Showcase handcrafted candle collections

Build a clean and elegant UI

Prepare structure for future scalability
-----
🚀 Future Improvements

Shopping cart functionality

Payment integration

Admin panel / CMS

Performance optimization

SEO impovements




[View Website](https://mimosa-atelier.onrender.com/)
-----

## Render Deploy Notes

- Build Command: `python manage.py collectstatic --noinput`
- Start Command: `gunicorn mimosa_backend.wsgi`
- Static files are served by WhiteNoise from the collected `staticfiles/` directory.
*** Add File: /Users/denysshepitko/Desktop/Проекты /html:css/Mimosa/mimosa_webshop/templates/includes/header.html
<header class="site-header">
	<div class="site-header__brand">
		<a href="{% url 'shop:home' %}" class="site-header__logo-link" aria-label="Mimosa home">
			<img src="{% static 'assets/images/logobl2.ico' %}" alt="Mimosa Logo" width="250" height="80">
		</a>
	</div>

	<nav class="site-header__nav" aria-label="Main navigation">
		<ul>
			<li><a href="{% url 'shop:home' %}" data-translate="nav-home">Home</a></li>
			{% if header_show_cart %}
			<li><a href="{% url 'shop:cart' %}">Cart ({{ cart_items_count }})</a></li>
			{% endif %}
			<li class="products-menu">
				<a href="{% url 'shop:products' %}" data-translate="nav-products">Products</a>
				<div class="dropdown-catalog" aria-label="Product categories">
					<a href="{% url 'shop:products' %}" class="dropdown-item" data-translate="nav-sub-all">All Products</a>
					<a href="{% url 'shop:product_bento' %}" class="dropdown-item" data-translate="nav-sub-bento">Bento Candles</a>
					<a href="{% url 'shop:products' %}" class="dropdown-item" data-translate="nav-sub-scented">Scented Candles</a>
					<a href="{% url 'shop:product_rose' %}" class="dropdown-item" data-translate="nav-sub-rose">Decorative Rose</a>
					<a href="{% url 'shop:products' %}" class="dropdown-item" data-translate="nav-sub-gifts">Gift Collections</a>
					<a href="{% url 'shop:products' %}" class="dropdown-item" data-translate="nav-sub-new">New Arrivals</a>
				</div>
			</li>
			<li><a href="{% url 'shop:about' %}" data-translate="nav-about">About Us</a></li>
			<li><a href="{% url 'shop:contact' %}" data-translate="nav-contact">Contact</a></li>
		</ul>
	</nav>

	<div class="site-header__tools">
		<div class="language-switcher" aria-label="Language switcher">
			<button class="lang-current" type="button" aria-label="Toggle language menu" aria-expanded="false">EN</button>
			<div class="lang-options" aria-label="Language options">
				<button class="lang-btn active" data-lang="en" title="English" type="button">EN</button>
				<button class="lang-btn" data-lang="fr" title="Français" type="button">FR</button>
				<button class="lang-btn" data-lang="ua" title="Українська" type="button">UA</button>
				<button class="lang-btn" data-lang="ru" title="Русский" type="button">RU</button>
			</div>
		</div>

		<a href="{% url 'shop:profile' %}" class="profile-icon" aria-label="Open profile">
			<svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
				<circle cx="12" cy="8" r="4" stroke="black" stroke-width="2"/>
				<path d="M4 20c0-4 4-6 8-6s8 2 8 6"
					stroke="black"
					stroke-width="2"
					stroke-linecap="round"/>
			</svg>
		</a>
	</div>
</header>

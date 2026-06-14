(function () {
    'use strict';

    var reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    function initScrollReveals() {
        if (reduceMotionQuery.matches) {
            document.querySelectorAll('.reveal-on-scroll').forEach(function (el) {
                el.classList.add('is-visible');
            });
            return;
        }

        if (!('IntersectionObserver' in window)) {
            return;
        }

        var revealSelectors = [
            'section.hero',
            'section.promo-banner',
            'section.about-snippet',
            'main h2.section-title',
            'main section',
            '.Products:not(.portfolio-masonry) > article',
            '.Products.portfolio-masonry > article:not(.Product4)',
            '.Products:not(.portfolio-masonry) .Product4',
            '.catalog-grid > article',
            '.catalog-card',
            '.cart-page section',
            '.cart-item',
            '.product-container',
            '.product-gallery',
            '.related-products',
            '.related-card',
            '.about-card',
            '.contact-item',
            '.contact-message',
            '.profile-hero-panel',
            '.profile-card',
            '.sv-hero',
            '.sv-section',
            '.newsletter-section'
        ];

        var textBlurSelector =
            'section.promo-banner, section.about-snippet, main h2.section-title, .sv-hero, .newsletter-section';

        var revealElements = document.querySelectorAll(revealSelectors.join(', '));

        if (!revealElements.length) {
            return;
        }

        var observer = new IntersectionObserver(
            function (entries, intersectionObserver) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        intersectionObserver.unobserve(entry.target);
                    }
                });
            },
            {
                root: null,
                threshold: 0.12,
                rootMargin: '0px 0px -8% 0px'
            }
        );

        revealElements.forEach(function (element) {
            element.classList.add('reveal-on-scroll');
            try {
                if (element.matches(textBlurSelector)) {
                    element.classList.add('reveal-on-scroll--text');
                }
            } catch (e) {
                /* older engines */
            }
            observer.observe(element);
        });
    }

    function initImageReveal() {
        document.querySelectorAll('.product-framed-image, .portfolio-card__media img').forEach(function (img) {
            if (img.complete) {
                img.classList.add('is-loaded');
                return;
            }
            img.addEventListener(
                'load',
                function () {
                    img.classList.add('is-loaded');
                },
                { once: true }
            );
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initScrollReveals();
        initImageReveal();
    });
})();

window.addEventListener('load', function () {
    document.body.classList.add('is-loaded');
});

(function () {
    'use strict';

    var reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    var isTouchViewport =
        window.matchMedia('(max-width: 767px)').matches ||
        window.matchMedia('(pointer: coarse)').matches;

    function markVisible(elements) {
        elements.forEach(function (el) {
            el.classList.add('reveal-on-scroll', 'is-visible');
        });
    }

    function initScrollReveals() {
        var revealSelectors = [
            'section.hero',
            'section.promo-banner',
            'section.about-snippet',
            'section.home-categories',
            'main h2.section-title',
            'main section:not(.portfolio-masonry)',
            '.Products:not(.portfolio-masonry) > article',
            '.Products.portfolio-masonry > article:not(.Product4)',
            '.Products:not(.portfolio-masonry) .Product4',
            '.catalog-grid > article',
            '.catalog-card',
            '.catalog-sidebar',
            '.catalog-content',
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

        var selector = revealSelectors.join(', ');

        if (reduceMotionQuery.matches || isTouchViewport) {
            document.querySelectorAll(selector).forEach(function (el) {
                el.classList.add('reveal-on-scroll', 'is-visible');
            });
            return;
        }

        if (!('IntersectionObserver' in window)) {
            markVisible(document.querySelectorAll(selector));
            return;
        }

        var textBlurSelector =
            'section.promo-banner, section.about-snippet, main h2.section-title, .sv-hero, .newsletter-section';

        var revealElements = document.querySelectorAll(selector);

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
                threshold: 0.08,
                rootMargin: '0px 0px 80px 0px'
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

    function markImageLoaded(img) {
        img.classList.add('is-loaded');
    }

    function initImageReveal() {
        document.querySelectorAll('.product-framed-image, .portfolio-card__media img, .catalog-card img').forEach(function (img) {
            if (isTouchViewport) {
                markImageLoaded(img);
                return;
            }

            if (img.complete && img.naturalWidth > 0) {
                markImageLoaded(img);
                return;
            }

            img.addEventListener(
                'load',
                function () {
                    markImageLoaded(img);
                },
                { once: true }
            );

            img.addEventListener(
                'error',
                function () {
                    markImageLoaded(img);
                },
                { once: true }
            );

            window.setTimeout(function () {
                markImageLoaded(img);
            }, 2500);
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

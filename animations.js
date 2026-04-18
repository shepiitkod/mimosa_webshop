(function () {
    'use strict';

    var reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    function initScrollReveals() {
        if (reduceMotionQuery.matches) {
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
            '.Products:not(.portfolio-masonry) .Product4',
            '.about-card',
            '.contact-item',
            '.contact-message',
            '.product-container',
            '.related-products',
            '.related-card',
            '.profile-hero-panel',
            '.profile-card'
        ];

        var textBlurSelector =
            'section.promo-banner, section.about-snippet, main h2.section-title';

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
                threshold: 0.1,
                rootMargin: '0px 0px -6% 0px'
            }
        );

        revealElements.forEach(function (element) {
            element.classList.add('reveal-on-scroll');
            try {
                if (element.matches(textBlurSelector)) {
                    element.classList.add('reveal-on-scroll--text');
                }
            } catch (e) {
                /* IE / very old engines without Element.matches */
            }
            observer.observe(element);
        });
    }

    document.addEventListener('DOMContentLoaded', initScrollReveals);
})();

window.addEventListener('load', function () {
    document.body.classList.add('is-loaded');
});

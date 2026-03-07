document.addEventListener('DOMContentLoaded', function () {
    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
        return;
    }

    var revealSelectors = [
        'main section',
        '.Products > article',
        '.Product4',
        '.about-card',
        '.contact-item',
        '.contact-message',
        '.product-container',
        '.related-products',
        '.related-card',
        '.profile-hero-panel',
        '.profile-card',
        '.hero',
        '.about-snippet'
    ];

    var revealElements = document.querySelectorAll(revealSelectors.join(', '));

    if (!revealElements.length || !('IntersectionObserver' in window)) {
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
        observer.observe(element);
    });
});

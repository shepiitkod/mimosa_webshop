(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function initDiscoverAtelier() {
        var root = document.querySelector('.discover');
        if (!root) return;

        var cards = Array.prototype.slice.call(
            root.querySelectorAll('.discover__card')
        );
        if (!cards.length) return;

        function reveal() {
            root.classList.add('is-inview');
            window.setTimeout(function () {
                root.classList.add('is-settled');
            }, 900);
        }

        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(
                function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) {
                            reveal();
                            observer.disconnect();
                        }
                    });
                },
                { threshold: 0.18, rootMargin: '0px 0px -8% 0px' }
            );
            observer.observe(root);
        } else {
            reveal();
        }

        if (reduceMotion.matches) {
            reveal();
            return;
        }

        cards.forEach(function (card) {
            var media = card.querySelector('.discover__card-media');
            if (!media) return;

            var frame = null;
            var target = { x: 0, y: 0 };
            var current = { x: 0, y: 0 };
            var hovering = false;

            function paint() {
                current.x += (target.x - current.x) * 0.1;
                current.y += (target.y - current.y) * 0.1;

                card.style.setProperty('--tilt-x', (-current.y * 3.2).toFixed(2) + 'deg');
                card.style.setProperty('--tilt-y', (current.x * 3.8).toFixed(2) + 'deg');
                card.style.setProperty('--pan-x', (current.x * 4).toFixed(2) + '%');
                card.style.setProperty('--pan-y', (current.y * 4).toFixed(2) + '%');

                if (
                    hovering ||
                    Math.abs(target.x - current.x) > 0.001 ||
                    Math.abs(target.y - current.y) > 0.001
                ) {
                    frame = window.requestAnimationFrame(paint);
                } else {
                    frame = null;
                }
            }

            function startPaint() {
                if (frame == null) frame = window.requestAnimationFrame(paint);
            }

            card.addEventListener('pointerenter', function () {
                hovering = true;
                startPaint();
            });

            card.addEventListener('pointermove', function (event) {
                var rect = card.getBoundingClientRect();
                target.x = clamp((event.clientX - rect.left) / rect.width - 0.5, -0.5, 0.5) * 2;
                target.y = clamp((event.clientY - rect.top) / rect.height - 0.5, -0.5, 0.5) * 2;
                startPaint();
            });

            card.addEventListener('pointerleave', function () {
                hovering = false;
                target.x = 0;
                target.y = 0;
                startPaint();
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDiscoverAtelier);
    } else {
        initDiscoverAtelier();
    }
})();

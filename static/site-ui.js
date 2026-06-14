(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    function initBackToTop() {
        var btn = document.getElementById('back-to-top');
        if (!btn) return;

        var visible = false;

        function updateVisibility() {
            var shouldShow = window.scrollY > 320;
            if (shouldShow === visible) return;
            visible = shouldShow;
            btn.classList.toggle('show', shouldShow);
        }

        window.addEventListener('scroll', updateVisibility, { passive: true });
        updateVisibility();

        btn.addEventListener('click', function () {
            if (reduceMotion.matches) {
                window.scrollTo(0, 0);
                return;
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    function initFabVisibility() {
        var fab = document.querySelector('.fab-consultation');
        if (!fab) return;

        var lastY = window.scrollY;
        var hidden = false;

        window.addEventListener(
            'scroll',
            function () {
                var y = window.scrollY;
                var scrollingDown = y > lastY + 6;
                var scrollingUp = y < lastY - 6;
                lastY = y;

                if (y < 120) {
                    if (hidden) {
                        hidden = false;
                        fab.classList.remove('fab-consultation--hidden');
                    }
                    return;
                }

                if (scrollingDown && !hidden) {
                    hidden = true;
                    fab.classList.add('fab-consultation--hidden');
                } else if (scrollingUp && hidden) {
                    hidden = false;
                    fab.classList.remove('fab-consultation--hidden');
                }
            },
            { passive: true }
        );
    }

    function initMobileMenuMotion() {
        var nav = document.getElementById('primary-navigation');
        if (!nav) return;

        document.addEventListener('keydown', function (e) {
            if (e.key !== 'Tab' || !document.body.classList.contains('kinetic-menu-open')) {
                return;
            }
            var focusable = nav.querySelectorAll(
                'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
            );
            if (!focusable.length) return;

            var first = focusable[0];
            var last = focusable[focusable.length - 1];

            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            initBackToTop();
            initFabVisibility();
            initMobileMenuMotion();
        });
    } else {
        initBackToTop();
        initFabVisibility();
        initMobileMenuMotion();
    }
})();

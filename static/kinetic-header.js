/**
 * Header helpers: magnetic nav links and mobile curtain menu.
 * Respects prefers-reduced-motion.
 */
(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    var header = document.getElementById('kinetic-header');
    if (!header) return;

    header.classList.remove('site-header--hidden', 'site-header--dock');
    header.classList.add('site-header--at-top');
    header.style.setProperty('--kinetic-scroll', '0');

    /* ——— Magnetic links (desktop) ——— */
    function initMagnetic() {
        if (reduceMotion.matches) return;
        if (window.matchMedia('(max-width: 900px)').matches) return;

        var links = header.querySelectorAll('.magnetic-link');
        var strength = 0.2;

        links.forEach(function (link) {
            link.addEventListener('mousemove', function (e) {
                var rect = link.getBoundingClientRect();
                var cx = rect.left + rect.width / 2;
                var cy = rect.top + rect.height / 2;
                var dx = (e.clientX - cx) * strength;
                var dy = (e.clientY - cy) * strength;
                link.style.transform = 'translate(' + dx + 'px, ' + dy + 'px)';
            });
            link.addEventListener('mouseleave', function () {
                link.style.transform = '';
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMagnetic);
    } else {
        initMagnetic();
    }

    /* ——— Mobile curtain ——— */
    var toggle = document.getElementById('kinetic-menu-toggle');
    var nav = document.getElementById('primary-navigation');

    function setMenuOpen(open) {
        document.body.classList.toggle('kinetic-menu-open', open);
        if (toggle) {
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        }
        document.body.style.overflow = open ? 'hidden' : '';
    }

    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            var open = !document.body.classList.contains('kinetic-menu-open');
            setMenuOpen(open);
        });

        nav.querySelectorAll('a').forEach(function (a) {
            a.addEventListener('click', function () {
                if (window.matchMedia('(max-width: 900px)').matches) {
                    setMenuOpen(false);
                }
            });
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && document.body.classList.contains('kinetic-menu-open')) {
                setMenuOpen(false);
            }
        });
    }
})();

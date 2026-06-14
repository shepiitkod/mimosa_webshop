/**
 * Header: scroll dock/hide, magnetic nav links, mobile curtain menu.
 * Respects prefers-reduced-motion.
 */
(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    var header = document.getElementById('kinetic-header');
    if (!header) return;

    var lastScrollY = window.scrollY || 0;
    var ticking = false;
    var hidden = false;
    var docked = false;

    function setHeaderState() {
        var y = window.scrollY || 0;
        var delta = y - lastScrollY;
        var atTop = y < 40;

        header.style.setProperty('--kinetic-scroll', String(Math.min(y / 600, 1)));

        if (atTop) {
            header.classList.add('site-header--at-top');
            header.classList.remove('site-header--dock', 'site-header--hidden');
            docked = false;
            hidden = false;
        } else {
            header.classList.remove('site-header--at-top');
            if (!docked) {
                header.classList.add('site-header--dock');
                docked = true;
            }

            if (!reduceMotion.matches && window.matchMedia('(max-width: 767px)').matches) {
                if (delta > 8 && y > 120 && !hidden) {
                    header.classList.add('site-header--hidden');
                    hidden = true;
                } else if (delta < -8 && hidden) {
                    header.classList.remove('site-header--hidden');
                    hidden = false;
                }
            } else {
                header.classList.remove('site-header--hidden');
                hidden = false;
            }
        }

        lastScrollY = y;
        ticking = false;
    }

    function onScroll() {
        if (!ticking) {
            ticking = true;
            window.requestAnimationFrame(setHeaderState);
        }
    }

    header.classList.remove('site-header--hidden');
    setHeaderState();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', setHeaderState, { passive: true });

    /* ——— Magnetic links (desktop) ——— */
    function initMagnetic() {
        if (reduceMotion.matches) return;
        if (window.matchMedia('(max-width: 767px)').matches) return;

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
        if (nav) {
            nav.setAttribute('aria-hidden', open ? 'false' : 'true');
            if (open) {
                var firstLink = nav.querySelector('a[href]');
                if (firstLink) {
                    window.setTimeout(function () {
                        firstLink.focus();
                    }, 120);
                }
            }
        }
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

        nav.addEventListener('click', function (e) {
            if (e.target === nav && window.matchMedia('(max-width: 767px)').matches) {
                setMenuOpen(false);
            }
        });

        nav.querySelectorAll('a').forEach(function (a) {
            a.addEventListener('click', function () {
                if (window.matchMedia('(max-width: 767px)').matches) {
                    setMenuOpen(false);
                }
            });
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && document.body.classList.contains('kinetic-menu-open')) {
                setMenuOpen(false);
            }
        });

        window.addEventListener('resize', function () {
            if (!window.matchMedia('(max-width: 767px)').matches) {
                setMenuOpen(false);
            }
        });

        setMenuOpen(false);
    }
})();

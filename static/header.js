/**
 * Site header: transparent over the homepage intro, solid elsewhere,
 * hides while scrolling down and returns on the way up. Boutique mega menu
 * (hover + keyboard) and the phone drawer (focus trap, Escape).
 */
(function () {
    'use strict';

    var header = document.querySelector('[data-header]');
    if (!header) return;

    var body = document.body;
    var overlay = header.classList.contains('mh--overlay');
    var intro = document.querySelector('[data-intro]');
    var lastY = window.scrollY || 0;
    var ticking = false;

    function update() {
        ticking = false;
        var y = window.scrollY || 0;
        var h = header.offsetHeight;
        header.classList.toggle('is-scrolled', y > 8);

        if (overlay) {
            var overIntro = intro ? intro.getBoundingClientRect().bottom > h : y < 8;
            header.classList.toggle('is-top', overIntro);
        }

        var menuOpen = body.classList.contains('kinetic-menu-open') || header.classList.contains('is-mega-open');
        if (!menuOpen) {
            if (y > lastY + 6 && y > 240) header.classList.add('is-hidden');
            else if (y < lastY - 6 || y < 240) header.classList.remove('is-hidden');
        }
        lastY = y;
        // Sticky bars below the header (boutique filters) follow it.
        var visible = header.classList.contains('is-hidden') ? 0 : Math.max(0, header.getBoundingClientRect().bottom);
        document.documentElement.style.setProperty('--mh-visible', visible + 'px');
        document.documentElement.style.setProperty('--mh-top', (header.getBoundingClientRect().bottom || h) + 'px');
    }

    window.addEventListener('scroll', function () {
        if (!ticking) {
            ticking = true;
            window.requestAnimationFrame(update);
        }
    }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();

    /* ---- Mega menu ---------------------------------------------------- */
    var mega = header.querySelector('[data-mega]');
    if (mega) {
        var trigger = mega.querySelector('[data-mega-trigger]');
        var panel = mega.querySelector('[data-mega-panel]');
        var closeTimer = null;
        var hoverable = window.matchMedia('(hover: hover) and (pointer: fine)');

        function setMega(open) {
            clearTimeout(closeTimer);
            mega.classList.toggle('is-open', open);
            header.classList.toggle('is-mega-open', open);
            trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
        }

        mega.addEventListener('mouseenter', function () {
            if (hoverable.matches) setMega(true);
        });
        mega.addEventListener('mouseleave', function () {
            if (!hoverable.matches) return;
            closeTimer = setTimeout(function () { setMega(false); }, 160);
        });
        // Keyboard / touch: first activation opens, second follows the link.
        trigger.addEventListener('click', function (e) {
            if (!mega.classList.contains('is-open')) {
                e.preventDefault();
                setMega(true);
                var first = panel.querySelector('a');
                if (first && e.detail === 0) first.focus();
            }
        });
        mega.addEventListener('focusout', function (e) {
            if (!mega.contains(e.relatedTarget)) setMega(false);
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && mega.classList.contains('is-open')) {
                setMega(false);
                trigger.focus();
            }
        });
        document.addEventListener('click', function (e) {
            if (!mega.contains(e.target)) setMega(false);
        });
    }

    /* ---- Phone drawer -------------------------------------------------- */
    var toggle = document.getElementById('mh-menu-toggle');
    var drawer = document.querySelector('[data-drawer]');
    if (!toggle || !drawer) return;

    function setDrawer(open) {
        body.classList.toggle('kinetic-menu-open', open);
        drawer.classList.toggle('is-open', open);
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        drawer.inert = !open;
        body.style.overflow = open ? 'hidden' : '';
        if (open) {
            header.classList.remove('is-hidden');
            var first = drawer.querySelector('summary, a[href]');
            if (first) setTimeout(function () { first.focus(); }, 80);
        }
    }

    drawer.inert = true;
    toggle.addEventListener('click', function () {
        setDrawer(!drawer.classList.contains('is-open'));
    });
    drawer.addEventListener('click', function (e) {
        if (e.target === drawer) setDrawer(false);
        if (e.target.closest('a[href]')) setDrawer(false);
    });
    document.addEventListener('keydown', function (e) {
        if (!drawer.classList.contains('is-open')) return;
        if (e.key === 'Escape') {
            setDrawer(false);
            toggle.focus();
            return;
        }
        if (e.key !== 'Tab') return;
        var items = [toggle].concat(Array.prototype.slice.call(
            drawer.querySelectorAll('summary, a[href], button:not([disabled])')
        ));
        var first = items[0];
        var last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
        }
    });
    window.addEventListener('resize', function () {
        if (window.matchMedia('(min-width: 1024px)').matches && drawer.classList.contains('is-open')) {
            setDrawer(false);
        }
    });
})();

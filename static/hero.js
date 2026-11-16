/**
 * MIMOSA — homepage hero, "le lookbook".
 *
 * The section holds still while you scroll; each plate turns over the
 * previous one from the right, like a page. Scrolling stays native (no
 * wheel hijacking): the plates simply follow window.scrollY.
 *
 * Performance: the section's position is measured once (and on resize),
 * never during scrolling; each frame only writes two transforms per plate
 * that moves, which the compositor handles without repainting the photos.
 */
(function () {
    'use strict';

    var root = document.querySelector('[data-hero]');
    if (!root) return;

    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var nums = root.querySelectorAll('[data-hero-num]');
    var caps = Array.prototype.slice.call(root.querySelectorAll('[data-cap]'));
    var plates = Array.prototype.slice.call(root.querySelectorAll('[data-plate]'));
    var ticks = Array.prototype.slice.call(root.querySelectorAll('[data-goto]'));
    var n = plates.length;
    if (n < 2) return;

    var pinned = document.documentElement.classList.contains('motion');
    var active = 0;
    var start = 0;      // scrollY where the section starts
    var travel = 1;     // scroll distance while the stage is pinned
    var last = [];      // last progress written per plate (skip identical writes)
    var ticking = false;
    var loaded = document.readyState === 'complete';

    function pad(n) {
        return (n < 9 ? '0' : '') + (n + 1);
    }

    function setActive(i) {
        if (i === active) return;
        active = i;
        nums.forEach(function (el) { el.textContent = pad(i); });
        caps.forEach(function (c, k) {
            c.hidden = k !== i;
            c.classList.toggle('is-active', k === i);
        });
        ticks.forEach(function (t, k) { t.classList.toggle('is-active', k === i); });
        plates.forEach(function (p, k) {
            if (k === i) p.removeAttribute('aria-hidden'); else p.setAttribute('aria-hidden', 'true');
        });
    }

    // Load the following plates early so a turned page never shows a blank,
    // but only once the page has loaded: the first photo comes first.
    function preload(upTo) {
        if (!loaded) return;
        for (var k = 0; k <= Math.min(n - 1, upTo); k++) {
            var img = plates[k].querySelector('img');
            if (img && img.loading === 'lazy') img.loading = 'eager';
        }
    }

    function write(k, e) {
        // e: 0 = still off to the right, 1 = fully turned.
        if (last[k] === e) return;
        last[k] = e;
        var x = ((1 - e) * 100).toFixed(3);
        plates[k].style.transform = e >= 1 ? 'none' : 'translate3d(' + x + '%,0,0)';
        plates[k].firstElementChild.style.transform = e >= 1 ? 'none' : 'translate3d(-' + x + '%,0,0)';
    }

    function ease(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

    function measure() {
        var rect = root.getBoundingClientRect();
        start = rect.top + window.scrollY;
        travel = Math.max(1, root.offsetHeight - window.innerHeight);
    }

    function update() {
        ticking = false;
        var p = Math.min(1, Math.max(0, (window.scrollY - start) / travel));
        var pos = p * (n - 1); // 0 .. n-1
        for (var k = 1; k < n; k++) {
            // Each page turns during its own slice of the scroll, then rests.
            var t = Math.min(1, Math.max(0, (pos - (k - 1)) / 0.8));
            write(k, Math.round(ease(t) * 1000) / 1000);
        }
        setActive(Math.min(n - 1, Math.round(pos)));
        preload(Math.ceil(pos) + 1);
    }

    function onScroll() {
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(update);
        }
    }

    function showInstant(i) {
        for (var k = 1; k < n; k++) write(k, k <= i ? 1 : 0);
        setActive(i);
        preload(i + 1);
    }

    ticks.forEach(function (t, k) {
        t.addEventListener('click', function () {
            if (!pinned) {
                showInstant(k);
                return;
            }
            measure();
            window.scrollTo({ top: start + travel * (k / (n - 1)) + 2, behavior: reduce ? 'auto' : 'smooth' });
        });
    });

    if (!pinned) {
        showInstant(0);
        return;
    }

    measure();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', function () { measure(); onScroll(); }, { passive: true });
    window.addEventListener('load', function () {
        loaded = true;
        measure();
        onScroll();
    });
    update();
})();

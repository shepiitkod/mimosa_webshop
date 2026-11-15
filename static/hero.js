/**
 * MIMOSA — homepage hero.
 *
 * A: the plate changes slowly by itself (crossfade + a slight zoom), with
 *    previous / pause / next controls. It never auto-advances with reduced
 *    motion, while the tab is hidden or while the hero is off screen.
 * B: the section holds still while you scroll; each plate is uncovered from
 *    the right over the previous one, like turning a lookbook page.
 *
 * Only photos and text move: opacity, transform, clip-path.
 */
(function () {
    'use strict';

    var root = document.querySelector('[data-hero]');
    if (!root) return;

    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var nums = root.querySelectorAll('[data-hero-num]');
    var caps = Array.prototype.slice.call(root.querySelectorAll('[data-cap]'));

    function pad(n) {
        return (n < 9 ? '0' : '') + (n + 1);
    }

    function showCaption(i) {
        nums.forEach(function (el) { el.textContent = pad(i); });
        caps.forEach(function (c, k) {
            var on = k === i;
            c.hidden = !on;
            c.classList.toggle('is-active', on);
        });
    }

    /* ------------------------------------------------------------------
       Variant A
       ------------------------------------------------------------------ */
    function initA() {
        var slides = Array.prototype.slice.call(root.querySelectorAll('[data-slide]'));
        if (slides.length < 2) return;
        var progress = root.querySelector('[data-hero-progress]');
        var pauseBtn = root.querySelector('[data-hero-pause]');
        var INTERVAL = 6000;
        var current = 0;
        var timer = null;
        var paused = reduce;
        var hovered = false;
        var visible = true;

        root.style.setProperty('--hero-interval', INTERVAL + 'ms');

        function go(i) {
            current = (i + slides.length) % slides.length;
            slides.forEach(function (s, k) {
                var on = k === current;
                s.classList.toggle('is-active', on);
                if (on) s.removeAttribute('aria-hidden'); else s.setAttribute('aria-hidden', 'true');
                // Start loading the next image before it is needed.
                if (k === (current + 1) % slides.length) {
                    var img = s.querySelector('img');
                    if (img && img.loading === 'lazy') img.loading = 'eager';
                }
            });
            showCaption(current);
            schedule();
        }

        function running() {
            return !paused && !hovered && visible && !document.hidden;
        }

        function schedule() {
            clearTimeout(timer);
            if (progress) {
                progress.classList.remove('is-running');
                // Restart the CSS progress line.
                void progress.offsetWidth;
            }
            if (!running()) return;
            if (progress) progress.classList.add('is-running');
            timer = setTimeout(function () { go(current + 1); }, INTERVAL);
        }

        root.querySelector('[data-hero-next]').addEventListener('click', function () { go(current + 1); });
        root.querySelector('[data-hero-prev]').addEventListener('click', function () { go(current - 1); });
        if (pauseBtn) {
            function label() {
                pauseBtn.setAttribute('aria-pressed', paused ? 'true' : 'false');
                var span = pauseBtn.querySelector('span');
                span.setAttribute('data-translate', paused ? 'hero2-play' : 'hero2-pause');
                if (typeof translations !== 'undefined') {
                    var lang = document.documentElement.lang || 'en';
                    var t = translations[lang] || {};
                    span.textContent = t[paused ? 'hero2-play' : 'hero2-pause'] || (paused ? 'Lecture' : 'Pause');
                } else {
                    span.textContent = paused ? 'Lecture' : 'Pause';
                }
            }
            pauseBtn.addEventListener('click', function () {
                paused = !paused;
                label();
                schedule();
            });
            label();
        }

        var frame = root.querySelector('[data-hero-frame]');
        frame.addEventListener('mouseenter', function () { hovered = true; schedule(); });
        frame.addEventListener('mouseleave', function () { hovered = false; schedule(); });
        root.addEventListener('focusin', function () { hovered = true; schedule(); });
        root.addEventListener('focusout', function () { hovered = false; schedule(); });
        document.addEventListener('visibilitychange', schedule);
        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (e) {
                visible = e[0].isIntersecting;
                schedule();
            }).observe(root);
        }
        // Give the first plate time to be seen before the first change.
        setTimeout(schedule, reduce ? 0 : 900);
    }

    /* ------------------------------------------------------------------
       Variant B
       ------------------------------------------------------------------ */
    function initB() {
        var plates = Array.prototype.slice.call(root.querySelectorAll('[data-plate]'));
        var ticks = Array.prototype.slice.call(root.querySelectorAll('[data-goto]'));
        var n = plates.length;
        if (n < 2) return;
        var pinned = document.documentElement.classList.contains('motion');
        var active = 0;
        var ticking = false;

        function setActive(i) {
            if (i === active) return;
            active = i;
            showCaption(i);
            ticks.forEach(function (t, k) { t.classList.toggle('is-active', k === i); });
            plates.forEach(function (p, k) {
                if (k === i) p.removeAttribute('aria-hidden'); else p.setAttribute('aria-hidden', 'true');
                if (k === i + 1) {
                    var img = p.querySelector('img');
                    if (img && img.loading === 'lazy') img.loading = 'eager';
                }
            });
        }

        function ease(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

        function update() {
            ticking = false;
            var rect = root.getBoundingClientRect();
            var travel = rect.height - window.innerHeight;
            var p = travel > 0 ? Math.min(1, Math.max(0, -rect.top / travel)) : 0;
            var pos = p * (n - 1);            // 0 .. n-1
            for (var k = 1; k < n; k++) {
                // Each plate turns during its own slice of the scroll, with a
                // short pause on every page.
                var t = Math.min(1, Math.max(0, (pos - (k - 1)) / 0.78));
                var e = ease(t);
                plates[k].style.clipPath = 'inset(0 0 0 ' + ((1 - e) * 100).toFixed(2) + '%)';
                plates[k].style.setProperty('--plate-scale', (1.06 - 0.06 * e).toFixed(4));
            }
            setActive(Math.min(n - 1, Math.round(pos)));
        }

        function showInstant(i) {
            plates.forEach(function (p, k) {
                p.style.clipPath = k <= i ? 'inset(0 0 0 0)' : 'inset(0 0 0 100%)';
            });
            setActive(i);
        }

        ticks.forEach(function (t, k) {
            t.addEventListener('click', function () {
                if (!pinned) {
                    showInstant(k);
                    return;
                }
                var travel = root.offsetHeight - window.innerHeight;
                var top = root.getBoundingClientRect().top + window.scrollY;
                window.scrollTo({ top: top + travel * (k / (n - 1)) + 2, behavior: reduce ? 'auto' : 'smooth' });
            });
        });

        if (!pinned) {
            showInstant(0);
            return;
        }
        window.addEventListener('scroll', function () {
            if (!ticking) {
                ticking = true;
                requestAnimationFrame(update);
            }
        }, { passive: true });
        window.addEventListener('resize', update, { passive: true });
        update();
    }

    if (root.getAttribute('data-hero') === 'b') initB(); else initA();
})();

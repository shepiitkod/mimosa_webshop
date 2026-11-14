/**
 * MIMOSA Atelier — motion.
 *
 * Everything here is built around candlelight: slow, precise, no fuss.
 * Only transform and opacity are animated. With prefers-reduced-motion
 * nothing moves and nothing stays hidden.
 *
 *  - legacy section reveals (catalog, cart, about…)
 *  - [data-reveal]          fade/rise in; [data-reveal="lines"] rises line by line
 *  - [data-parallax="0.08"] photo drifts and settles while scrolling
 *  - [data-creations]       horizontal showcase pinned to vertical scroll (desktop)
 *  - [data-gestes]          "Fait main à Nîmes" steps swap the picture on scroll
 *  - warm cursor light      desktop with a mouse only
 *  - smooth wheel scrolling desktop with a mouse only
 */
(function () {
    'use strict';

    var reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    var reduce = reduceMotionQuery.matches;
    var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    var isTouchViewport =
        window.matchMedia('(max-width: 767px)').matches ||
        window.matchMedia('(pointer: coarse)').matches;

    if (!reduce) {
        document.documentElement.classList.add('js-motion');
    }

    function clamp(v, a, b) {
        return Math.min(b, Math.max(a, v));
    }

    /* ------------------------------------------------------------------
       Legacy reveals for the inner pages (CSS lives in styles.css)
       ------------------------------------------------------------------ */
    function initScrollReveals() {
        var selector = [
            'main section:not([data-own-motion]):not(.portfolio-masonry):not(.discover):not(.welcome-float)',
            '.Products:not(.portfolio-masonry) > article',
            '.cart-page section',
            '.cart-item',
            '.product-container',
            '.related-products',
            '.about-card',
            '.contact-item',
            '.contact-message',
            '.profile-hero-panel',
            '.profile-card',
            '.sv-hero',
            '.sv-section',
            '.newsletter-section'
        ].join(', ');

        var elements = document.querySelectorAll(selector);
        if (!elements.length) return;

        if (reduce || isTouchViewport || !('IntersectionObserver' in window)) {
            elements.forEach(function (el) {
                el.classList.add('reveal-on-scroll', 'is-visible');
            });
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.08, rootMargin: '0px 0px 80px 0px' });

        elements.forEach(function (el) {
            el.classList.add('reveal-on-scroll');
            observer.observe(el);
        });
    }

    function initImageReveal() {
        document.querySelectorAll('.product-framed-image').forEach(function (img) {
            function done() { img.classList.add('is-loaded'); }
            if (isTouchViewport || (img.complete && img.naturalWidth > 0)) {
                done();
                return;
            }
            img.addEventListener('load', done, { once: true });
            img.addEventListener('error', done, { once: true });
            window.setTimeout(done, 2500);
        });
    }

    /* ------------------------------------------------------------------
       Line-by-line text reveal
       Words are wrapped in masks (inline markup such as <em> is kept);
       words that share a line get the same --line index, so each line
       rises as one.
       ------------------------------------------------------------------ */
    function splitWords(root) {
        var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
        var nodes = [];
        while (walker.nextNode()) nodes.push(walker.currentNode);
        nodes.forEach(function (node) {
            var parts = node.nodeValue.split(/(\s+)/);
            if (parts.length === 1 && !parts[0].trim()) return;
            var frag = document.createDocumentFragment();
            parts.forEach(function (part) {
                if (!part) return;
                if (/^\s+$/.test(part)) {
                    frag.appendChild(document.createTextNode(' '));
                    return;
                }
                var outer = document.createElement('span');
                outer.className = 'rw';
                var inner = document.createElement('span');
                inner.className = 'rwi';
                inner.textContent = part;
                outer.appendChild(inner);
                frag.appendChild(outer);
            });
            node.parentNode.replaceChild(frag, node);
        });
    }

    function assignLines(root) {
        var words = root.querySelectorAll('.rw');
        var line = -1;
        var lastTop = null;
        words.forEach(function (w) {
            var top = w.offsetTop;
            if (lastTop === null || Math.abs(top - lastTop) > 4) {
                line += 1;
                lastTop = top;
            }
            w.style.setProperty('--line', line);
        });
    }

    function prepareLines(el) {
        if (el.querySelector('.rw')) return;
        splitWords(el);
        assignLines(el);
    }

    function initReveals() {
        var items = document.querySelectorAll('[data-reveal]');
        if (!items.length) return;

        if (reduce || !('IntersectionObserver' in window)) {
            items.forEach(function (el) { el.classList.add('is-in'); });
            return;
        }

        // Stagger siblings that enter together.
        items.forEach(function (el) {
            if (el.getAttribute('data-reveal') === 'lines') prepareLines(el);
        });

        var observer = new IntersectionObserver(function (entries) {
            var batch = 0;
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.style.setProperty('--reveal-delay', (batch * 0.12) + 's');
                batch += 1;
                entry.target.classList.add('is-in');
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.15, rootMargin: '0px 0px -6% 0px' });

        items.forEach(function (el) { observer.observe(el); });

        var relayout;
        window.addEventListener('resize', function () {
            clearTimeout(relayout);
            relayout = setTimeout(function () {
                document.querySelectorAll('[data-reveal="lines"]').forEach(assignLines);
            }, 200);
        }, { passive: true });

        // Translation replaces the text: wrap the new words again.
        document.addEventListener('mimosa:lang', function () {
            document.querySelectorAll('[data-reveal="lines"]').forEach(prepareLines);
        });
    }

    /* ------------------------------------------------------------------
       Scroll loop shared by parallax and the horizontal showcase
       ------------------------------------------------------------------ */
    var scrollTasks = [];
    var scheduled = false;

    function runScrollTasks() {
        scheduled = false;
        var y = window.scrollY || window.pageYOffset || 0;
        var vh = window.innerHeight;
        for (var i = 0; i < scrollTasks.length; i++) scrollTasks[i](y, vh);
    }

    function requestScrollTasks() {
        if (!scheduled) {
            scheduled = true;
            window.requestAnimationFrame(runScrollTasks);
        }
    }

    function initParallax() {
        if (reduce) return;
        var items = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
        if (!items.length) return;

        var visible = new Set();
        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (e) {
                    if (e.isIntersecting) visible.add(e.target); else visible.delete(e.target);
                });
                requestScrollTasks();
            }, { rootMargin: '10% 0px' });
            items.forEach(function (el) { io.observe(el); });
        } else {
            items.forEach(function (el) { visible.add(el); });
        }

        scrollTasks.push(function (y, vh) {
            visible.forEach(function (el) {
                var img = el.querySelector('img');
                if (!img) return;
                var r = el.getBoundingClientRect();
                // -1 when the block enters at the bottom, +1 when it leaves at the top.
                var p = clamp(((r.top + r.height / 2) - vh / 2) / (vh / 2 + r.height / 2), -1, 1);
                var f = parseFloat(el.getAttribute('data-parallax')) || 0.06;
                var shift = p * f * r.height;
                var scale = 1 + f * (0.6 + 0.4 * Math.abs(p));
                img.style.transform = 'translate3d(0,' + shift.toFixed(1) + 'px,0) scale(' + scale.toFixed(3) + ')';
            });
        });
    }

    /* ------------------------------------------------------------------
       Nos Créations: horizontal showcase pinned to the vertical scroll
       ------------------------------------------------------------------ */
    function initCreations() {
        var section = document.querySelector('[data-creations]');
        if (!section) return;
        var track = section.querySelector('.creations__track');
        var cards = Array.prototype.slice.call(section.querySelectorAll('.creation'));
        var counter = section.querySelector('.creations__progress-now');
        if (!track || !cards.length) return;

        var desktop = window.matchMedia('(min-width: 768px)');
        var distance = 0;
        var active = -1;

        function setActive(i) {
            if (i === active) return;
            active = i;
            var tint = cards[i].getAttribute('data-tint');
            if (tint) section.style.setProperty('--tint', 'var(--tint-' + tint + ')');
            if (counter) counter.textContent = (i < 9 ? '0' : '') + (i + 1);
        }

        function layout() {
            if (reduce || !desktop.matches) {
                section.classList.remove('is-pinned');
                section.style.height = '';
                track.style.removeProperty('--x');
                return;
            }
            section.classList.add('is-pinned');
            distance = Math.max(0, track.scrollWidth - window.innerWidth);
            section.style.height = (window.innerHeight + distance) + 'px';
            requestScrollTasks();
        }

        scrollTasks.push(function (y, vh) {
            if (!section.classList.contains('is-pinned')) return;
            var top = section.getBoundingClientRect().top;
            var p = clamp(-top / Math.max(1, distance), 0, 1);
            track.style.setProperty('--x', (-p * distance).toFixed(1) + 'px');
            setActive(Math.round(p * (cards.length - 1)));
        });

        // Phones: tint follows the card in view inside the swipe row.
        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (entries) {
                if (section.classList.contains('is-pinned')) return;
                entries.forEach(function (e) {
                    if (e.isIntersecting) setActive(cards.indexOf(e.target));
                });
            }, { root: track, threshold: 0.6 });
            cards.forEach(function (c) { io.observe(c); });
        }

        setActive(0);
        layout();
        window.addEventListener('resize', layout, { passive: true });
        window.addEventListener('load', layout);
    }

    /* ------------------------------------------------------------------
       Fait main à Nîmes: the step in the middle of the screen wins
       ------------------------------------------------------------------ */
    function initGestes() {
        var section = document.querySelector('[data-gestes]');
        if (!section || !('IntersectionObserver' in window)) return;
        var steps = section.querySelectorAll('[data-step]');
        var imgs = section.querySelectorAll('[data-step-img]');
        var now = section.querySelector('[data-step-now]');

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (!e.isIntersecting) return;
                var i = e.target.getAttribute('data-step');
                steps.forEach(function (s) { s.classList.toggle('is-active', s === e.target); });
                imgs.forEach(function (im) {
                    im.classList.toggle('is-active', im.getAttribute('data-step-img') === i);
                });
                if (now) now.textContent = '0' + (parseInt(i, 10) + 1);
            });
        }, { rootMargin: '-45% 0px -45% 0px' });

        steps.forEach(function (s) { io.observe(s); });
    }

    /* ------------------------------------------------------------------
       Warm light under the cursor (mouse devices only)
       ------------------------------------------------------------------ */
    function initCursorGlow() {
        if (reduce || !finePointer) return;
        var glow = document.createElement('div');
        glow.className = 'cursor-glow';
        glow.setAttribute('aria-hidden', 'true');
        document.body.appendChild(glow);

        var tx = window.innerWidth / 2;
        var ty = window.innerHeight / 2;
        var x = tx;
        var y = ty;
        var running = false;

        function frame() {
            x += (tx - x) * 0.12;
            y += (ty - y) * 0.12;
            glow.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0)';
            if (Math.abs(tx - x) > 0.3 || Math.abs(ty - y) > 0.3) {
                window.requestAnimationFrame(frame);
            } else {
                running = false;
            }
        }

        document.addEventListener('mousemove', function (e) {
            tx = e.clientX;
            ty = e.clientY;
            glow.classList.add('is-on');
            if (!running) {
                running = true;
                window.requestAnimationFrame(frame);
            }
        }, { passive: true });

        document.documentElement.addEventListener('mouseleave', function () {
            glow.classList.remove('is-on');
        });
    }

    /* ------------------------------------------------------------------
       Smooth wheel scrolling (mouse devices only). Keyboard, scrollbar,
       anchors and trackpad momentum keep working natively.
       ------------------------------------------------------------------ */
    function canScrollInside(node, deltaY, deltaX) {
        while (node && node !== document.body && node !== document.documentElement) {
            if (node.nodeType === 1) {
                var cs = window.getComputedStyle(node);
                if (Math.abs(deltaX) > Math.abs(deltaY)) {
                    if (/(auto|scroll)/.test(cs.overflowX) && node.scrollWidth > node.clientWidth) return true;
                } else if (/(auto|scroll)/.test(cs.overflowY) && node.scrollHeight > node.clientHeight) {
                    if ((deltaY < 0 && node.scrollTop > 0) ||
                        (deltaY > 0 && node.scrollTop + node.clientHeight < node.scrollHeight)) return true;
                }
            }
            node = node.parentNode;
        }
        return false;
    }

    function initSmoothScroll() {
        if (reduce || !finePointer) return;
        var target = window.scrollY;
        var current = window.scrollY;
        var animating = false;

        function maxScroll() {
            return document.documentElement.scrollHeight - window.innerHeight;
        }

        function step() {
            current += (target - current) * 0.11;
            if (Math.abs(target - current) < 0.5) {
                current = target;
                animating = false;
            }
            window.scrollTo(0, current);
            if (animating) window.requestAnimationFrame(step);
        }

        window.addEventListener('wheel', function (e) {
            if (e.ctrlKey || e.defaultPrevented) return;
            // Pixel-precise trackpads already feel smooth; leave them alone.
            if (e.deltaMode === 0 && Math.abs(e.deltaY) < 40 && !animating) return;
            if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
            if (document.body.classList.contains('kinetic-menu-open')) return;
            if (canScrollInside(e.target, e.deltaY, e.deltaX)) return;

            e.preventDefault();
            var delta = e.deltaY * (e.deltaMode === 1 ? 32 : e.deltaMode === 2 ? window.innerHeight : 1);
            if (!animating) {
                target = window.scrollY;
                current = window.scrollY;
            }
            target = clamp(target + delta, 0, maxScroll());
            if (!animating) {
                animating = true;
                window.requestAnimationFrame(step);
            }
        }, { passive: false });

        window.addEventListener('scroll', function () {
            if (!animating) {
                target = window.scrollY;
                current = window.scrollY;
            }
        }, { passive: true });
    }

    function init() {
        initScrollReveals();
        initImageReveal();
        initReveals();
        initParallax();
        initCreations();
        initGestes();
        initCursorGlow();
        initSmoothScroll();
        window.addEventListener('scroll', requestScrollTasks, { passive: true });
        window.addEventListener('resize', requestScrollTasks, { passive: true });
        requestScrollTasks();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

window.addEventListener('load', function () {
    document.body.classList.add('is-loaded');
});

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
        // The consultation button stays out of the way on the first screen
        // (so it never covers the hero CTA) and fades in once the visitor
        // has scrolled past it. It hides again near the footer.
        var fab = document.querySelector('.fab-consultation');
        if (!fab) return;

        var ticking = false;

        function update() {
            ticking = false;
            var y = window.scrollY || 0;
            var vh = window.innerHeight || 800;
            var docH = document.documentElement.scrollHeight;
            var pastHero = y > vh * 0.8;
            var nearEnd = y + vh > docH - 260;
            fab.classList.toggle('fab-consultation--visible', pastHero && !nearEnd);
        }

        window.addEventListener('scroll', function () {
            if (!ticking) {
                ticking = true;
                window.requestAnimationFrame(update);
            }
        }, { passive: true });
        window.addEventListener('resize', update, { passive: true });
        update();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            initBackToTop();
            initFabVisibility();
        });
    } else {
        initBackToTop();
        initFabVisibility();
    }
})();

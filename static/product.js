/**
 * Product page: gallery (swipe / thumbnails), hover zoom on desktop,
 * full-screen lightbox, quantity stepper and the phone buy bar.
 */
(function () {
    'use strict';

    var gallery = document.querySelector('[data-gallery]');
    var track = gallery && gallery.querySelector('[data-gallery-track]');
    var slides = track ? Array.prototype.slice.call(track.querySelectorAll('.pdp-gallery__slide')) : [];
    var thumbs = gallery ? Array.prototype.slice.call(gallery.querySelectorAll('.thumbnail')) : [];
    var dots = gallery ? Array.prototype.slice.call(gallery.querySelectorAll('.pdp-gallery__dots span')) : [];
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var current = 0;

    function setActive(i) {
        current = i;
        thumbs.forEach(function (t, k) { t.classList.toggle('active', k === i); });
        dots.forEach(function (d, k) { d.classList.toggle('is-active', k === i); });
    }

    function goTo(i) {
        if (!track || !slides[i]) return;
        track.scrollTo({ left: slides[i].offsetLeft, behavior: reduce ? 'auto' : 'smooth' });
        setActive(i);
    }

    if (track && slides.length) {
        thumbs.forEach(function (t, k) {
            t.addEventListener('click', function () { goTo(k); });
        });
        var raf = null;
        track.addEventListener('scroll', function () {
            if (raf) return;
            raf = requestAnimationFrame(function () {
                raf = null;
                var i = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
                if (i !== current) setActive(Math.max(0, Math.min(slides.length - 1, i)));
            });
        }, { passive: true });
    }

    /* ---- Hover zoom (desktop with a mouse) --------------------------- */
    var container = document.getElementById('zoomContainer');
    var lens = document.getElementById('zoomLens');
    var result = document.getElementById('zoomResult');
    var fine = window.matchMedia('(hover: hover) and (pointer: fine) and (min-width: 1101px)');
    var ZOOM = 2.6;

    function currentImg() {
        return slides[current] ? slides[current].querySelector('img') : null;
    }

    function hideZoom() {
        if (lens) lens.style.display = 'none';
        if (result) result.style.display = 'none';
    }

    if (container && lens && result) {
        container.addEventListener('mouseenter', function () {
            if (!fine.matches) return;
            var img = currentImg();
            if (!img) return;
            lens.style.display = 'block';
            result.style.display = 'block';
            result.style.backgroundImage = 'url("' + (img.currentSrc || img.src) + '")';
        });
        container.addEventListener('mouseleave', hideZoom);
        container.addEventListener('mousemove', function (e) {
            if (!fine.matches) return;
            var img = currentImg();
            if (!img) return;
            var box = img.getBoundingClientRect();
            var cbox = container.getBoundingClientRect();
            var lw = result.offsetWidth / ZOOM;
            var lh = result.offsetHeight / ZOOM;
            var x = Math.max(0, Math.min(e.clientX - box.left - lw / 2, box.width - lw));
            var y = Math.max(0, Math.min(e.clientY - box.top - lh / 2, box.height - lh));
            lens.style.width = lw + 'px';
            lens.style.height = lh + 'px';
            lens.style.left = (box.left - cbox.left + x) + 'px';
            lens.style.top = (box.top - cbox.top + y) + 'px';
            result.style.backgroundSize = (box.width * ZOOM) + 'px ' + (box.height * ZOOM) + 'px';
            result.style.backgroundPosition = (-x * ZOOM) + 'px ' + (-y * ZOOM) + 'px';
        });
    }

    /* ---- Lightbox ------------------------------------------------------ */
    var box = document.querySelector('[data-lightbox]');
    var boxImg = box && box.querySelector('[data-lightbox-img]');

    function showInBox(i) {
        if (!boxImg || !slides[i]) return;
        current = (i + slides.length) % slides.length;
        boxImg.src = slides[current].getAttribute('data-full');
    }

    if (box && boxImg && typeof box.showModal === 'function') {
        slides.forEach(function (s, k) {
            s.addEventListener('click', function () {
                hideZoom();
                showInBox(k);
                box.showModal();
            });
        });
        box.querySelector('[data-lightbox-close]').addEventListener('click', function () { box.close(); });
        box.querySelectorAll('[data-lightbox-step]').forEach(function (b) {
            b.hidden = slides.length < 2;
            b.addEventListener('click', function () {
                showInBox(current + parseInt(b.getAttribute('data-lightbox-step'), 10));
            });
        });
        box.addEventListener('click', function (e) { if (e.target === box) box.close(); });
        box.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowRight') showInBox(current + 1);
            if (e.key === 'ArrowLeft') showInBox(current - 1);
        });
        box.addEventListener('close', function () { goTo(current); });
    }

    /* ---- Quantity ------------------------------------------------------ */
    document.querySelectorAll('[data-qty]').forEach(function (q) {
        var input = q.querySelector('input');
        q.querySelectorAll('[data-qty-step]').forEach(function (b) {
            b.addEventListener('click', function () {
                var v = (parseInt(input.value, 10) || 1) + parseInt(b.getAttribute('data-qty-step'), 10);
                input.value = Math.max(1, Math.min(99, v));
            });
        });
    });

    /* ---- Phone buy bar ------------------------------------------------- */
    var sticky = document.querySelector('[data-buy-sticky]');
    var mainBtn = document.querySelector('[data-buy-main]');
    if (sticky && mainBtn && 'IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
            // Visible whenever the main button is off screen (above or below).
            sticky.classList.toggle('is-visible', !entries[0].isIntersecting);
        }).observe(mainBtn);
    }
})();

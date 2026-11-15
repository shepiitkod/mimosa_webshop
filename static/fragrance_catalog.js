/**
 * Seconde vie — fragrance table.
 * The table is rendered by Django (all data, visible without JS). This file
 * only: filters and sorts without reloading (keeping the URL shareable),
 * opens a row to show its description, and translates the small labels the
 * phone layout prints before each value.
 */
(function () {
    'use strict';

    var root = document.querySelector('[data-ft]');
    if (!root) return;

    var form = root.querySelector('[data-ft-filters]');
    var table = root.querySelector('.ft-table');
    var items = Array.prototype.slice.call(root.querySelectorAll('[data-ft-item]'));
    var countEl = root.querySelector('[data-ft-count]');
    var emptyEl = root.querySelector('[data-ft-empty]');
    var resetEl = root.querySelector('[data-ft-reset]');
    var BANDS = { legere: [1, 2], moyenne: [3, 3], intense: [4, 5] };

    root.classList.add('is-enhanced');

    /* ---- Opening rows ---------------------------------------------------- */
    function setOpen(item, open) {
        var btn = item.querySelector('[data-ft-toggle]');
        var detail = item.querySelector('[data-ft-detail]');
        item.classList.toggle('is-open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        detail.hidden = !open;
    }

    items.forEach(function (item) {
        setOpen(item, false);
        item.querySelector('.ft-row').addEventListener('click', function (e) {
            if (e.target.closest('a')) return;
            setOpen(item, !item.classList.contains('is-open'));
        });
    });

    // Opening the page on #parfum-xxx shows that fragrance open.
    if (location.hash.indexOf('#parfum-') === 0) {
        var target = document.getElementById(location.hash.slice(1));
        if (target && target.hasAttribute('data-ft-item')) setOpen(target, true);
    }

    /* ---- Filters and sorting -------------------------------------------- */
    function apply(pushUrl) {
        var data = new FormData(form);
        var famille = data.get('famille') || '';
        var intensite = data.get('intensite') || '';
        var saison = data.get('saison') || '';
        var tri = data.get('tri') || '';
        var band = BANDS[intensite];
        var shown = 0;

        items.forEach(function (item) {
            var level = parseInt(item.getAttribute('data-intensity'), 10);
            var seasons = (item.getAttribute('data-seasons') || '').split(' ');
            var ok =
                (!famille || item.getAttribute('data-family') === famille) &&
                (!band || (level >= band[0] && level <= band[1])) &&
                (!saison || seasons.indexOf(saison) !== -1);
            item.hidden = !ok;
            if (ok) shown += 1;
        });

        var sorted = items.slice().sort(function (a, b) {
            var na = a.getAttribute('data-name');
            var nb = b.getAttribute('data-name');
            var ia = parseInt(a.getAttribute('data-intensity'), 10);
            var ib = parseInt(b.getAttribute('data-intensity'), 10);
            if (tri === 'nom') return na.localeCompare(nb, 'fr');
            if (tri === 'intensite-asc') return ia - ib || na.localeCompare(nb, 'fr');
            if (tri === 'intensite-desc') return ib - ia || na.localeCompare(nb, 'fr');
            return parseInt(a.getAttribute('data-position'), 10) - parseInt(b.getAttribute('data-position'), 10);
        });
        sorted.forEach(function (item) { table.appendChild(item); });

        if (countEl) countEl.textContent = shown;
        if (emptyEl) emptyEl.hidden = shown > 0;
        var filtered = !!(famille || intensite || saison || tri);
        if (resetEl) resetEl.hidden = !filtered;

        if (pushUrl && window.history && history.replaceState) {
            var params = new URLSearchParams();
            if (famille) params.set('famille', famille);
            if (intensite) params.set('intensite', intensite);
            if (saison) params.set('saison', saison);
            if (tri) params.set('tri', tri);
            var qs = params.toString();
            history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + '#parfums');
        }
    }

    form.classList.add('is-live');
    form.addEventListener('change', function () { apply(true); });
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        apply(true);
    });
    if (resetEl) {
        resetEl.addEventListener('click', function (e) {
            e.preventDefault();
            form.reset();
            Array.prototype.forEach.call(form.querySelectorAll('select'), function (s) { s.value = ''; });
            apply(true);
        });
    }

    /* ---- Labels of the phone cards follow the language ------------------ */
    function translateLabels() {
        if (typeof translations === 'undefined') return;
        var lang = document.documentElement.lang || 'en';
        var t = translations[lang] || {};
        root.querySelectorAll('[data-label-key]').forEach(function (cell) {
            var v = t[cell.getAttribute('data-label-key')];
            if (v) cell.setAttribute('data-label', v);
        });
    }

    document.addEventListener('mimosa:lang', translateLabels);
    translateLabels();
})();

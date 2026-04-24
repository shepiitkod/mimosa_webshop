/**
 * Mimosa — dynamic shipping (zone, weight, carrier) + checkout UX (toast, loading, debug).
 */
(function () {
    const DEBUG = typeof window.MIMOSA_SHIPPING_DEBUG !== 'undefined' && window.MIMOSA_SHIPPING_DEBUG;

    function ensureToastHost() {
        let host = document.getElementById('shipping-toast-host');
        if (!host) {
            host = document.createElement('div');
            host.id = 'shipping-toast-host';
            host.className = 'shipping-toast-host';
            host.setAttribute('aria-live', 'polite');
            document.body.appendChild(host);
        }
        return host;
    }

    function showToast(text, level) {
        const host = ensureToastHost();
        const el = document.createElement('div');
        el.className = 'shipping-toast shipping-toast--' + (level || 'info');
        el.setAttribute('role', 'status');
        el.textContent = text;
        host.appendChild(el);
        requestAnimationFrame(() => el.classList.add('shipping-toast--visible'));
        const ttl = level === 'error' ? 9000 : 6000;
        setTimeout(() => {
            el.classList.remove('shipping-toast--visible');
            setTimeout(() => el.remove(), 400);
        }, ttl);
    }

    window.MimosaShippingToast = showToast;

    const toastDataEl = document.getElementById('shipping-toast-messages');
    if (toastDataEl) {
        try {
            const arr = JSON.parse(toastDataEl.textContent);
            if (Array.isArray(arr)) {
                arr.forEach((t) => {
                    const level = (t.level || 'info').toLowerCase();
                    const normalized = level.includes('error')
                        ? 'error'
                        : level.includes('success')
                          ? 'success'
                          : 'info';
                    showToast(t.text || '', normalized);
                });
            }
        } catch (err) {
            if (DEBUG) console.warn('Toast parse error', err);
        }
    }

    const checkoutForm = document.querySelector('[data-checkout-form]');
    const checkoutBtn = document.querySelector('[data-checkout-submit]');
    if (checkoutForm && checkoutBtn) {
        checkoutForm.addEventListener('submit', () => {
            if (checkoutBtn.disabled) return;
            checkoutBtn.disabled = true;
            checkoutBtn.classList.add('is-loading');
            checkoutBtn.setAttribute('aria-busy', 'true');
        });
    }

    const rulesEl = document.getElementById('shipping-rules-data');
    const cartEl = document.getElementById('cart-lines-data');
    const root = document.querySelector('[data-shipping-root]');
    if (!rulesEl || !cartEl || !root) return;

    let shippingConfig;
    try {
        shippingConfig = JSON.parse(rulesEl.textContent);
    } catch (e) {
        return;
    }

    let cartLines;
    try {
        cartLines = JSON.parse(cartEl.textContent);
    } catch (e) {
        cartLines = [];
    }

    const THRESHOLD = Number(shippingConfig.freeShippingThresholdEur) || 85;
    const MAX_W = Number(shippingConfig.maxStandardWeightG) || 2000;
    const OVERSIZED = shippingConfig.oversizedCarrierId || 'oversized';
    const pricesEur = shippingConfig.pricesEur || {};
    const carrierMeta = shippingConfig.carrierMeta || {};
    const countryGroups = shippingConfig.countryGroups || {};

    function getZone(iso) {
        const c = (iso || '').toUpperCase();
        if (countryGroups.FR && countryGroups.FR.some((x) => x.iso === c)) return 'FR';
        if (countryGroups.EU && countryGroups.EU.some((x) => x.iso === c)) return 'EU';
        return 'INTL';
    }

    function weightBandIndex(grams) {
        const g = Math.max(1, Number(grams) || 1);
        if (g < 500) return 0;
        if (g < 1000) return 1;
        return 2;
    }

    function carriersForZone(zone) {
        if (zone === 'FR') return ['chronopost', 'colissimo', 'mondial_relay'];
        if (zone === 'EU' || zone === 'INTL') return ['chronopost', 'colissimo'];
        return [];
    }

    function carriersForCart(zone, totalWeight) {
        if (totalWeight > MAX_W) return [OVERSIZED];
        return carriersForZone(zone);
    }

    /** Matches shop.shipping.oversized_shipping_eur (ceil blocks × Colissimo tier 2). */
    function oversizedChargeEur(zone, totalWeight) {
        if (totalWeight <= MAX_W) return null;
        const row = pricesEur[zone] && pricesEur[zone].colissimo;
        if (!row || !row.length) return null;
        const tier2 = Number(row[2]);
        if (!Number.isFinite(tier2)) return null;
        const blocks = Math.ceil(Number(totalWeight) / 2000);
        return tier2 * blocks;
    }

    function basePriceEur(zone, carrier, band) {
        const row = (pricesEur[zone] && pricesEur[zone][carrier]) || null;
        if (!row) return null;
        const b = Math.min(Math.max(band, 0), row.length - 1);
        return Number(row[b]);
    }

    function isFreeStandard(zone, carrier, subtotal) {
        if (zone !== 'FR') return false;
        if (subtotal < THRESHOLD) return false;
        return carrier === 'colissimo' || carrier === 'mondial_relay';
    }

    function chargedEur(zone, carrier, band, subtotal) {
        const base = basePriceEur(zone, carrier, band);
        if (base == null) return null;
        if (isFreeStandard(zone, carrier, subtotal)) return 0;
        return base;
    }

    function cartTotals() {
        let sub = 0;
        let w = 0;
        cartLines.forEach((line) => {
            const qty = Number(line.quantity) || 0;
            const lt = Number(String(line.lineTotal).replace(',', '.')) || 0;
            sub += lt;
            w += (Number(line.weightGrams) || 200) * qty;
        });
        return { subtotal: sub, totalWeight: Math.max(w, 1) };
    }

    function formatEur(n) {
        return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(n);
    }

    function shippingChargeNow() {
        const { subtotal, totalWeight } = cartTotals();
        const zone = getZone(selectedIso);
        if (totalWeight > MAX_W) {
            if (selectedCarrier !== OVERSIZED) return null;
            const o = oversizedChargeEur(zone, totalWeight);
            return o == null ? null : o;
        }
        const band = weightBandIndex(totalWeight);
        const c = chargedEur(zone, selectedCarrier, band, subtotal);
        return c;
    }

    function logShippingDebug(extra) {
        if (!DEBUG) return;
        const { subtotal, totalWeight } = cartTotals();
        const zone = getZone(selectedIso);
        const oversized = totalWeight > MAX_W;
        const ship = shippingChargeNow();
        const row = {
            zone,
            totalWeightG: totalWeight,
            maxStandardG: MAX_W,
            mode: oversized ? 'oversized' : 'standard',
            weightBand: oversized ? '—' : weightBandIndex(totalWeight),
            carrier: selectedCarrier,
            shippingEur: ship == null ? '—' : Number(ship.toFixed(2)),
            subtotalEur: Number(subtotal.toFixed(2)),
            grandEur: ship == null ? '—' : Number((subtotal + ship).toFixed(2)),
            ...extra,
        };
        console.table([row]);
    }

    const hiddenCountry = root.querySelector('[data-shipping-country-input]');
    const hiddenCarrier = root.querySelector('[data-shipping-carrier-input]');
    const countryBtn = root.querySelector('[data-country-button]');
    const countryPanel = root.querySelector('[data-country-panel]');
    const countryLabel = root.querySelector('[data-country-label]');
    const carriersEl = root.querySelector('[data-carrier-cards]');
    const elSubtotal = root.querySelector('[data-summary-subtotal]');
    const elShipping = root.querySelector('[data-summary-shipping]');
    const elGrand = root.querySelector('[data-summary-grand]');
    const elFreeHint = root.querySelector('[data-free-hint]');

    let selectedIso = hiddenCountry && hiddenCountry.value ? hiddenCountry.value : 'FR';
    let selectedCarrier = hiddenCarrier && hiddenCarrier.value ? hiddenCarrier.value : '';

    function countryLabelFor(iso) {
        const all = []
            .concat(countryGroups.FR || [], countryGroups.EU || [], countryGroups.INTL || [])
            .find((x) => x.iso === iso);
        return all ? all.label : iso;
    }

    function buildCountryPanel() {
        if (!countryPanel) return;
        countryPanel.innerHTML = '';
        const sections = [
            { key: 'FR', title: 'France' },
            { key: 'EU', title: 'European Union' },
            { key: 'INTL', title: 'International' },
        ];
        sections.forEach((sec) => {
            const rows = countryGroups[sec.key];
            if (!rows || !rows.length) return;
            const gl = document.createElement('div');
            gl.className = 'shipping-country__group-label';
            gl.textContent = sec.title;
            countryPanel.appendChild(gl);
            rows.forEach((row) => {
                const b = document.createElement('button');
                b.type = 'button';
                b.className = 'shipping-country__option';
                b.dataset.value = row.iso;
                b.textContent = row.label;
                if (row.iso === selectedIso) b.classList.add('is-active');
                b.addEventListener('click', () => {
                    const newIso = row.iso;
                    const newZone = getZone(newIso);
                    const tw = cartTotals().totalWeight;
                    const allowedIds = carriersForCart(newZone, tw);

                    selectedIso = newIso;
                    if (hiddenCountry) hiddenCountry.value = selectedIso;
                    if (countryLabel) countryLabel.textContent = countryLabelFor(selectedIso);
                    countryPanel.querySelectorAll('.shipping-country__option').forEach((n) => {
                        n.classList.toggle('is-active', n.dataset.value === selectedIso);
                    });

                    if (!selectedCarrier || !allowedIds.includes(selectedCarrier)) {
                        selectedCarrier = '';
                        if (hiddenCarrier) hiddenCarrier.value = '';
                    }

                    closeCountry();
                    renderCarriers();
                });
                countryPanel.appendChild(b);
            });
        });
    }

    function closeCountry() {
        if (!countryPanel || !countryBtn) return;
        countryPanel.classList.remove('is-open');
        countryBtn.setAttribute('aria-expanded', 'false');
    }

    function toggleCountry() {
        if (!countryPanel || !countryBtn) return;
        const open = !countryPanel.classList.contains('is-open');
        countryPanel.classList.toggle('is-open', open);
        countryBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    function renderCarriers() {
        if (!carriersEl) return;
        const { subtotal, totalWeight } = cartTotals();
        const zone = getZone(selectedIso);
        const heavy = totalWeight > MAX_W;

        carriersEl.innerHTML = '';

        if (heavy) {
            const charge = oversizedChargeEur(zone, totalWeight);
            selectedCarrier = OVERSIZED;
            if (hiddenCarrier) hiddenCarrier.value = OVERSIZED;

            const meta = carrierMeta[OVERSIZED] || {
                name: 'Colis lourd (+2 kg)',
                eta: 'Tarif majoré par tranche de 2 kg (base Colissimo)',
            };
            const card = document.createElement('div');
            card.className = 'shipping-carrier-card shipping-carrier-card--info is-active';
            card.setAttribute('role', 'status');
            const priceText = charge == null ? '—' : formatEur(charge);
            card.innerHTML = `
                <div class="shipping-carrier-card__row">
                    <div class="shipping-carrier-card__main">
                        <div class="shipping-carrier-card__name">${meta.name}</div>
                        <div class="shipping-carrier-card__eta">${meta.eta}</div>
                    </div>
                    <div class="shipping-carrier-card__price-wrap">
                        <span class="shipping-carrier-card__price">${priceText}</span>
                    </div>
                </div>`;
            carriersEl.appendChild(card);

            if (elFreeHint) {
                elFreeHint.textContent =
                    'Au-delà de 2 kg, les offres standard sont remplacées par un tarif automatique par tranche de 2 kg (aligné sur Colissimo, tranche max).';
            }
            updateTotals();
            logShippingDebug({ note: 'oversized-only' });
            return;
        }

        const carriers = carriersForZone(zone);
        const band = weightBandIndex(totalWeight);

        const priced = carriers
            .map((id) => {
                const base = basePriceEur(zone, id, band);
                const charge = chargedEur(zone, id, band, subtotal);
                if (base == null || charge == null) return null;
                return { id, base, charge };
            })
            .filter(Boolean);

        priced.sort((a, b) => a.charge - b.charge || a.id.localeCompare(b.id));

        if (!selectedCarrier || !priced.some((p) => p.id === selectedCarrier)) {
            selectedCarrier = priced.length ? priced[0].id : '';
            if (hiddenCarrier) hiddenCarrier.value = selectedCarrier;
        }

        priced.forEach((p) => {
            const meta = carrierMeta[p.id] || { name: p.id, eta: '' };
            const card = document.createElement('button');
            card.type = 'button';
            card.className = 'shipping-carrier-card' + (p.id === selectedCarrier ? ' is-active' : '');
            card.dataset.carrier = p.id;
            card.setAttribute('role', 'radio');
            card.setAttribute('aria-checked', p.id === selectedCarrier ? 'true' : 'false');

            const free = isFreeStandard(zone, p.id, subtotal);
            const priceHtml = free
                ? `<div class="shipping-carrier-card__price-wrap">
                     <span class="shipping-carrier-card__price is-struck">${formatEur(p.base)}</span>
                     <span class="shipping-carrier-card__gratuit" aria-label="Gratuit">Gratuit</span>
                   </div>`
                : `<div class="shipping-carrier-card__price-wrap">
                     <span class="shipping-carrier-card__price">${formatEur(p.charge)}</span>
                   </div>`;

            card.innerHTML = `
                <div class="shipping-carrier-card__row">
                    <div class="shipping-carrier-card__main">
                        <div class="shipping-carrier-card__name">${meta.name}</div>
                        <div class="shipping-carrier-card__eta">${meta.eta || ''}</div>
                    </div>
                    ${priceHtml}
                </div>`;

            card.addEventListener('click', () => {
                selectedCarrier = p.id;
                if (hiddenCarrier) hiddenCarrier.value = selectedCarrier;
                renderCarriers();
            });
            carriersEl.appendChild(card);
        });

        updateTotals();
        if (elFreeHint) {
            const zf = getZone(selectedIso) === 'FR';
            elFreeHint.textContent =
                zf && subtotal < THRESHOLD
                    ? `Livraison gratuite dès ${THRESHOLD} € d’achat (France).`
                    : zf && subtotal >= THRESHOLD
                      ? 'Livraison gratuite appliquée aux options standard (Colissimo, Mondial Relay).'
                      : '';
        }
        logShippingDebug({ note: 'standard' });
    }

    function updateTotals() {
        const { subtotal, totalWeight } = cartTotals();
        const zone = getZone(selectedIso);
        let ship = 0;

        if (totalWeight > MAX_W) {
            if (selectedCarrier === OVERSIZED) {
                const o = oversizedChargeEur(zone, totalWeight);
                ship = o == null ? 0 : o;
            }
        } else {
            const band = weightBandIndex(totalWeight);
            const c = chargedEur(zone, selectedCarrier, band, subtotal);
            ship = c == null ? 0 : c;
        }

        if (elSubtotal) elSubtotal.textContent = formatEur(subtotal);
        if (elShipping) elShipping.textContent = formatEur(ship);
        if (elGrand) elGrand.textContent = formatEur(subtotal + ship);
    }

    if (countryBtn && countryPanel) {
        countryBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleCountry();
        });
        document.addEventListener('click', () => closeCountry());
        countryPanel.addEventListener('click', (e) => e.stopPropagation());
    }

    if (countryLabel) countryLabel.textContent = countryLabelFor(selectedIso);
    buildCountryPanel();
    renderCarriers();

    window.shippingConfig = {
        zones: ['FR', 'EU', 'INTL'],
        carriers: ['chronopost', 'colissimo', 'mondial_relay', OVERSIZED],
        weights: ['<500g', '500g-1kg', '1-2kg', `>${MAX_W}g oversized`],
        pricesEur,
        freeShippingThresholdEur: THRESHOLD,
        maxStandardWeightG: MAX_W,
    };
})();

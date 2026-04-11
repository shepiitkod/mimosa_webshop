/**
 * Bento candle color swatches: updates #mainProductImage src from data-main-src.
 */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    const root = document.querySelector('.bento-color-picker');
    if (!root) return;

    const main = document.getElementById('mainProductImage');
    if (!main) return;

    const swatches = root.querySelectorAll('.bento-swatch');

    function setActive(activeBtn) {
      swatches.forEach(function (btn) {
        btn.classList.toggle('is-active', btn === activeBtn);
        btn.setAttribute('aria-checked', btn === activeBtn ? 'true' : 'false');
      });
    }

    swatches.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const src = btn.getAttribute('data-main-src');
        if (src) main.src = src;
        setActive(btn);
      });
    });
  });
})();

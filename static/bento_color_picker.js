/**
 * Bento candle color swatches: visual selection only (highlights active button).
 */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    const root = document.querySelector('.bento-color-picker');
    if (!root) return;

    const swatches = root.querySelectorAll('.bento-swatch');

    function setActive(activeBtn) {
      swatches.forEach(function (btn) {
        btn.classList.toggle('is-active', btn === activeBtn);
        btn.setAttribute('aria-checked', btn === activeBtn ? 'true' : 'false');
      });
    }

    swatches.forEach(function (btn) {
      btn.addEventListener('click', function () {
        setActive(btn);
      });
    });
  });
})();

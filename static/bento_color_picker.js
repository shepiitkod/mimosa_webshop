/**
 * Bento candle color swatches: visual selection only (highlights active button).
 */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    const root = document.querySelector('.bento-color-picker');
    if (!root) return;

    const swatches = root.querySelectorAll('.bento-swatch');
    const colorNameInput = document.getElementById('selectedColorName');
    const colorHexInput = document.getElementById('selectedColorHex');

    function setActive(activeBtn) {
      swatches.forEach(function (btn) {
        btn.classList.toggle('is-active', btn === activeBtn);
        btn.setAttribute('aria-checked', btn === activeBtn ? 'true' : 'false');
      });
      if (colorNameInput) colorNameInput.value = activeBtn.dataset.colorName || '';
      if (colorHexInput) colorHexInput.value = activeBtn.dataset.colorHex || '';
    }

    const initial = root.querySelector('.bento-swatch.is-active') || swatches[0];
    if (initial) setActive(initial);

    swatches.forEach(function (btn) {
      btn.addEventListener('click', function () {
        setActive(btn);
      });
    });
  });
})();

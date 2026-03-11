document.addEventListener('DOMContentLoaded', function () {
    document.body.classList.add('admin-loaded');

    // Add a subtle staggered reveal to cards/modules for better perceived responsiveness.
    const blocks = document.querySelectorAll('.card, .module, .small-box');
    blocks.forEach(function (el, index) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(6px)';
        el.style.transition = 'opacity 220ms ease, transform 220ms ease';
        window.setTimeout(function () {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, Math.min(index * 35, 280));
    });
});

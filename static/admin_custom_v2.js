document.addEventListener('DOMContentLoaded', function () {
    // Force light theme for a clean, readable admin UI.
    localStorage.setItem('theme', 'light');
    document.documentElement.setAttribute('data-theme', 'light');
    document.documentElement.classList.remove('theme-dark');
    document.documentElement.classList.add('theme-light');
});

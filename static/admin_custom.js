document.addEventListener('DOMContentLoaded', function () {
    // Force Django admin light theme (prevents persistent dark mode from localStorage).
    localStorage.setItem('theme', 'light');
    document.documentElement.setAttribute('data-theme', 'light');
    document.documentElement.classList.remove('theme-dark');
    document.documentElement.classList.add('theme-light');
});

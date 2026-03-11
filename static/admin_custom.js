document.addEventListener('DOMContentLoaded', function () {
    // Keep admin consistently in dark mode for the Mimosa dark dashboard look.
    localStorage.setItem('theme', 'dark');
    document.documentElement.setAttribute('data-theme', 'dark');
    document.documentElement.classList.remove('theme-light');
    document.documentElement.classList.add('theme-dark');
});

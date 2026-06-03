/**
 * Mimosa Admin Dashboard JavaScript
 * Handles greetings, counter animations, and interactive features
 */

// ═══════════════════════════════════════════════════════════════════════════════════
// Greeting System
// ═══════════════════════════════════════════════════════════════════════════════════

const GREETINGS = {
    morning: [
        "Доброе утро, {name}! Время продуктивной работы. ☀️",
        "Утренний кофе заряжен, привет, {name}! ☕",
        "С добрым утром, {name}! Начнём продуктивный день? 🌅",
        "Доброе утро, {name}! Вот свежая статистика ночи. 📊",
        "Привет, {name}! Утро дарует новые возможности! 🚀",
    ],
    afternoon: [
        "Добрый день, {name}! Как идут продажи? 📈",
        "Рады видеть тебя, {name}! Обеденный перерыв? 🍽️",
        "День в разгаре, {name}! Вот свежая статистика. 💼",
        "Привет, {name}! Полдень — время подвести итоги. ⏰",
        "Добрый день, {name}! Очередная волна заказов? 🌊",
    ],
    evening: [
        "Добрый вечер, {name}! Подводим итоги дня? 🌙",
        "Вечер, {name}! Смотрим, что получилось сегодня. 👀",
        "Привет, {name}! Скоро конец рабочего дня, сводки готовы? 📋",
        "Добрый вечер, {name}! Как день? 🌃",
        "Вечер, {name}! Время подвести итоги и отдохнуть. 🎯",
    ],
    night: [
        "Ночной дозор, {name}! Не спится? 🌃",
        "{name}, совы работают! Ночная смена включена? 🦉",
        "Привет, {name}! Ночь молода, продолжаем работать? 🌙",
        "Полночь, {name}! Отчеты могут подождать? 😴",
        "{name}, это ночь! Не забудь про отдых. 💤",
    ]
};

/**
 * Determine period based on hour and return greeting data
 */
function getPeriodGreeting() {
    const hour = new Date().getHours();
    let period, icon;

    if (hour >= 6 && hour < 12) {
        period = 'morning';
        icon = '🌅';
    } else if (hour >= 12 && hour < 18) {
        period = 'afternoon';
        icon = '☀️';
    } else if (hour >= 18 && hour < 24) {
        period = 'evening';
        icon = '🌙';
    } else {
        period = 'night';
        icon = '🌃';
    }

    const greetingList = GREETINGS[period];
    const randomGreeting = greetingList[Math.floor(Math.random() * greetingList.length)];

    return { text: randomGreeting, icon, period };
}

function getAdminName() {
    const greetingTextEl = document.getElementById('greetingText');
    const name = greetingTextEl?.dataset.adminName?.trim();
    return name || 'Admin';
}

// ═══════════════════════════════════════════════════════════════════════════════════
// Counter Animation
// ═══════════════════════════════════════════════════════════════════════════════════

/**
 * Animate counter from 0 to target value
 * @param {HTMLElement} element - Target element
 * @param {number} target - Target value
 * @param {number} duration - Animation duration in ms
 */
function animateCounter(element, target, duration = 1500) {
    const startTime = performance.now();
    const startValue = 0;
    const suffix = element.getAttribute('data-suffix') || '';

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Cubic-out easing function for natural feel
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.floor(startValue + (target - startValue) * easeProgress);

        // Format with locale-specific number formatting
        element.textContent = currentValue.toLocaleString('uk-UA') + suffix;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            // Ensure final value is exact
            element.textContent = target.toLocaleString('uk-UA') + suffix;
        }
    }

    requestAnimationFrame(update);
}

/**
 * Start all counter animations on page load
 */
function startCounterAnimations() {
    const counters = document.querySelectorAll('[data-counter]');
    counters.forEach((counter) => {
        const target = parseInt(counter.getAttribute('data-counter'), 10);
        if (!isNaN(target)) {
            animateCounter(counter, target, 1500);
        }
    });
}

// ═══════════════════════════════════════════════════════════════════════════════════
// Initialization
// ═══════════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {
    // Update greeting
    const { text, icon } = getPeriodGreeting();
    const adminName = getAdminName();
    const greetingTextEl = document.getElementById('greetingText');
    const greetingIconEl = document.getElementById('greetingIcon');
    const greetingTimeEl = document.getElementById('greetingTime');

    if (greetingTextEl) greetingTextEl.textContent = text.replaceAll('{name}', adminName);
    if (greetingIconEl) greetingIconEl.textContent = icon;
    if (greetingTimeEl) {
        greetingTimeEl.textContent = 'Добро пожаловать в панель управления Mimosa Atelier';
    }

    // Start animations
    startCounterAnimations();
});

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getPeriodGreeting,
        animateCounter,
        startCounterAnimations,
    };
}

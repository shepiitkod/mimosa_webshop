document.addEventListener('DOMContentLoaded', () => {
    const stage = document.querySelector('.auth-stage');
    if (!stage) {
        return;
    }

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reducedMotion) {
        return;
    }

    const isMobile = window.matchMedia('(max-width: 860px)').matches;
    const lowPower = navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4;
    const petalsCount = isMobile || lowPower ? 8 : 14;

    for (let i = 0; i < petalsCount; i += 1) {
        const petal = document.createElement('span');
        petal.className = 'auth-petal';

        const left = Math.random() * 100;
        const delay = Math.random() * 8;
        const duration = (isMobile ? 12 : 10) + Math.random() * (isMobile ? 8 : 9);
        const drift = -30 + Math.random() * 60;
        const scale = 0.7 + Math.random() * 0.8;

        petal.style.left = `${left}%`;
        petal.style.animationDelay = `${delay}s`;
        petal.style.animationDuration = `${duration}s`;
        petal.style.setProperty('--petal-drift', `${drift}px`);
        petal.style.transform = `scale(${scale}) rotate(45deg)`;

        stage.appendChild(petal);
    }
});

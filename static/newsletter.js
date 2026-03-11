/**
 * Newsletter Subscription Handler
 * Handles AJAX form submission for newsletter subscriptions
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('newsletter-form');
    const emailInput = document.getElementById('newsletter-email');
    const messageDiv = document.getElementById('newsletter-message');
    const submitBtn = form ? form.querySelector('button[type="submit"]') : null;

    if (!form) return;

    // Helper function to get current language
    function getCurrentLanguage() {
        return localStorage.getItem('selectedLanguage') || 'en';
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const email = emailInput.value.trim();

        // Validate email
        if (!email) {
            showMessage(getTranslation('newsletter-email-required', 'Email is required.'), 'error');
            return;
        }

        if (!isValidEmail(email)) {
            showMessage(getTranslation('newsletter-invalid-email', 'Please enter a valid email address.'), 'error');
            return;
        }

        // Disable button during submission
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.6';
        }

        try {
            const response = await fetch('/newsletter/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ email: email }),
            });

            const data = await response.json();

            if (data.success) {
                const successMsg = getTranslation('newsletter-success', 'Thank you for joining our journey!');
                showMessage(successMsg, 'success');
                
                // Clear form
                emailInput.value = '';
                
                // Keep success message visible for 5 seconds
                setTimeout(function() {
                    messageDiv.innerHTML = '';
                    messageDiv.className = '';
                }, 5000);
            } else {
                let errorMsg = data.error || getTranslation('newsletter-generic-error', 'Something went wrong. Please try again.');

                if (errorMsg.includes('already')) {
                    errorMsg = getTranslation('newsletter-already-subscribed', 'You are already subscribed with this email.');
                } else if (errorMsg.includes('valid') || errorMsg.includes('format')) {
                    errorMsg = getTranslation('newsletter-invalid-email', 'Please enter a valid email address.');
                }

                showMessage(errorMsg, 'error');
            }
        } catch (error) {
            console.error('Newsletter subscription error:', error);
            showMessage(getTranslation('newsletter-network-error', 'Network error. Please try again.'), 'error');
        } finally {
            // Re-enable button
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
            }
        }
    });

    /**
     * Display message with animation
     */
    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = 'newsletter-message ' + type;
    }

    function getTranslation(key, fallback) {
        if (typeof translations === 'undefined') {
            return fallback;
        }

        const lang = getCurrentLanguage();
        return (translations[lang] && translations[lang][key]) || fallback;
    }

    /**
     * Validate email format
     */
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Get CSRF token from cookies
     */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

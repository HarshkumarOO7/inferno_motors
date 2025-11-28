// login.js
// Handles flipping the card between Login and Signup.
// Also uses progressive enhancement: links are real anchors, JS enhances by flipping instead of navigating.

document.addEventListener('DOMContentLoaded', function () {
    const flipToSignup = document.getElementById('flipToSignup');
    const flipToLogin = document.getElementById('flipToLogin');
    const card = document.getElementById('card');
    const cardFront = document.getElementById('cardFront');
    const cardBack = document.getElementById('cardBack');

    // Helper: apply ARIA and classes for visible side
    function showSignup() {
        card.classList.add('flipped');
        cardFront.setAttribute('aria-hidden', 'true');
        cardBack.setAttribute('aria-hidden', 'false');
    }
    function showLogin() {
        card.classList.remove('flipped');
        cardFront.setAttribute('aria-hidden', 'false');
        cardBack.setAttribute('aria-hidden', 'true');
    }

    // If elements exist, prevent default anchor behavior and flip instead
    if (flipToSignup) {
        flipToSignup.addEventListener('click', function (e) {
            // If link points to actual signup page but we want to flip,
            // prevent navigation and flip the card.
            e.preventDefault();
            showSignup();
            // optionally update browser history (so back button returns to login)
            if (history && history.pushState) {
                history.pushState({ authCard: 'signup' }, '', '#signup');
            }
        });
    }

    if (flipToLogin) {
        flipToLogin.addEventListener('click', function (e) {
            e.preventDefault();
            showLogin();
            if (history && history.pushState) {
                history.pushState({ authCard: 'login' }, '', '#login');
            }
        });
    }

    // Respect hash on load: if user opened page with #signup, show signup
    if (window.location.hash === '#signup') {
        showSignup();
    } else if (window.location.hash === '#login') {
        showLogin();
    }

    // Handle popstate (back/forward navigation)
    window.addEventListener('popstate', function (ev) {
        try {
            if (ev.state && ev.state.authCard === 'signup') showSignup();
            else showLogin();
        } catch (e) { /* ignore */ }
    });

    // Accessibility: keyboard toggle (optional)
    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') { // ctrl/cmd+k to toggle
            if (card.classList.contains('flipped')) showLogin(); else showSignup();
        }
    });
});

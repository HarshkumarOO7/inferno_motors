// ----------------------------
// Card Flip & Form Helpers
// ----------------------------

/**
 * Safe query helper (returns element or null)
 */
const $ = (sel) => document.getElementById(sel) || document.querySelector(sel);

/**
 * Add event listener only when element exists
 */
function on(el, evt, fn) {
  if (!el) return;
  el.addEventListener(evt, fn);
}

/**
 * Toggle flipped class on the card
 */
const card = $('#card');
function setFlipped(on) {
  if (!card) return;
  card.classList.toggle('flipped', !!on);
}

/**
 * Simple loading state for a button (adds disabled + data-loading attribute)
 */
function setButtonLoading(btn, loading = true) {
  if (!btn) return;
  btn.disabled = loading;
  if (loading) {
    btn.dataset.loading = 'true';
    // store original text so we can restore
    if (!btn.dataset.origText) btn.dataset.origText = btn.innerHTML;
    btn.innerHTML = 'Please wait…';
    btn.classList.add('loading');
  } else {
    btn.disabled = false;
    btn.classList.remove('loading');
    btn.innerHTML = btn.dataset.origText || btn.innerHTML;
  }
}

// ----------------------------
// Flip controls (guarded)
// ----------------------------
on($('#flipToSignup'), (e) => { e.preventDefault(); setFlipped(true); });
on($('#flipToLogin'),  (e) => { e.preventDefault(); setFlipped(false); });

// nav-flip ids might not exist — check selectors (support both id and nav links)
on($('#flipToSignupNav'), (e) => { e.preventDefault(); setFlipped(true); });
on($('#flipToLoginNav'),  (e) => { e.preventDefault(); setFlipped(false); });

// Allow using anchor links like ".flip-to-signup" if you used classes instead
document.querySelectorAll('.flip-to-signup').forEach(el => on(el, 'click', (e) => { e.preventDefault(); setFlipped(true); }));
document.querySelectorAll('.flip-to-login').forEach(el => on(el, 'click', (e) => { e.preventDefault(); setFlipped(false); }));

// Close the card with Escape key
on(document, 'keyup', (e) => {
  if (e.key === 'Escape') setFlipped(false);
});

// ----------------------------
// Form Submission Logic — keep normal submit (no AJAX here)
// ----------------------------

const loginForm = $('#loginForm');
const signupForm = $('#signupForm');

function attachFormSubmit(form) {
  if (!form) return;

  // find submit button(s) inside the form
  const submitButtons = Array.from(form.querySelectorAll('[type="submit"]'));
  const primaryBtn = submitButtons[0] || null;

  // on submit: disable the button to prevent accidental double-clicks and let the browser submit
  on(form, 'submit', (evt) => {
    // basic client-side validation hint: if HTML required attributes fail, the browser will block submit
    // here we only guard double submit and provide feedback
    if (primaryBtn) setButtonLoading(primaryBtn, true);

    // NOTE: do NOT call evt.preventDefault(); we want the browser to perform the normal POST so Django can
    // validate CSRF token and handle the request server-side.
    // If you later implement AJAX, add proper CSRF token handling (see Django docs).
  });

  // Re-enable button if user leaves the page or form is reset
  on(form, 'reset', () => { if (primaryBtn) setButtonLoading(primaryBtn, false); });
  // In case user navigates back and the button stayed disabled, also try to re-enable on focus
  if (primaryBtn) {
    on(primaryBtn, 'focus', () => setButtonLoading(primaryBtn, false));
  }
}

attachFormSubmit(loginForm);
attachFormSubmit(signupForm);

// ----------------------------
// Optional: small accessibility improvement
// ----------------------------
document.querySelectorAll('input[required]').forEach(inp => {
  inp.addEventListener('invalid', () => {
    // bring focus to the first invalid field
    inp.focus();
  }, { once: true });
});

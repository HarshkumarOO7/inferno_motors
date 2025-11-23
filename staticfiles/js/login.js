// Card Flip Logic
const card = document.getElementById('card');
const flipToSignup = document.getElementById('flipToSignup');
const flipToLogin = document.getElementById('flipToLogin');
const flipToSignupNav = document.getElementById('flipToSignupNav');
const flipToLoginNav = document.getElementById('flipToLoginNav');

flipToSignup.addEventListener('click', (e) => {
    e.preventDefault();
    card.classList.add('flipped');
});

flipToLogin.addEventListener('click', (e) => {
    e.preventDefault();
    card.classList.remove('flipped');
});

flipToSignupNav.addEventListener('click', (e) => {
    e.preventDefault();
    card.classList.add('flipped');
});

flipToLoginNav.addEventListener('click', (e) => {
    e.preventDefault();
    card.classList.remove('flipped');
});

// Form Submission Logic
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');

loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    alert('Login Successful!');
    // Add your login logic here
});

signupForm.addEventListener('submit', (e) => {
    e.preventDefault();
    alert('Signup Successful!');
    // Add your signup logic here
});
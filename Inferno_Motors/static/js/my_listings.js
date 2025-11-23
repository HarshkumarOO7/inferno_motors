document.addEventListener('DOMContentLoaded', function() {
    // Animate listings on scroll
    const animateOnScroll = function() {
        const listings = document.querySelectorAll('.listing-card');

        listings.forEach((listing, index) => {
            const listingPosition = listing.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;

            if (listingPosition < screenPosition) {
                setTimeout(() => {
                    listing.style.opacity = '1';
                    listing.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    };

    // Set initial state for animations
    const listings = document.querySelectorAll('.listing-card');
    listings.forEach(listing => {
        listing.style.opacity = '0';
        listing.style.transform = 'translateY(20px)';
        listing.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });

    // Run on load and scroll
    animateOnScroll();
    window.addEventListener('scroll', animateOnScroll);

    // Add hover effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 5px 15px rgba(243, 156, 18, 0.4)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });

    // Add ripple effect to buttons
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const x = e.clientX - e.target.getBoundingClientRect().left;
            const y = e.clientY - e.target.getBoundingClientRect().top;

            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 1000);
        });
    });

    // Add dark mode toggle (optional)
    const darkModeToggle = document.createElement('div');
    darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    darkModeToggle.style.position = 'fixed';
    darkModeToggle.style.bottom = '20px';
    darkModeToggle.style.right = '20px';
    darkModeToggle.style.background = 'var(--primary)';
    darkModeToggle.style.color = '#121212';
    darkModeToggle.style.width = '50px';
    darkModeToggle.style.height = '50px';
    darkModeToggle.style.borderRadius = '50%';
    darkModeToggle.style.display = 'flex';
    darkModeToggle.style.justifyContent = 'center';
    darkModeToggle.style.alignItems = 'center';
    darkModeToggle.style.cursor = 'pointer';
    darkModeToggle.style.boxShadow = '0 4px 10px rgba(0,0,0,0.2)';
    darkModeToggle.style.zIndex = '1000';
    darkModeToggle.style.transition = 'all 0.3s ease';

    darkModeToggle.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
    });

    darkModeToggle.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
    });

    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('light-mode');
        if (document.body.classList.contains('light-mode')) {
            this.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            this.innerHTML = '<i class="fas fa-moon"></i>';
        }
    });

    document.body.appendChild(darkModeToggle);
});

// Add ripple effect styles dynamically
const style = document.createElement('style');
style.innerHTML = `
    .ripple {
        position: absolute;
        background: rgba(255, 255, 255, 0.4);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }

    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .light-mode {
        --dark: #f5f5f5;
        --dark-light: #ffffff;
        --text: #333333;
        --text-secondary: #666666;
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
`;
document.head.appendChild(style);
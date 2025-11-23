/**
 * Car Selling Platform - JavaScript Module
 * Handles all frontend interactions for the car selling platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all car selling functionality
    initCarSellingPlatform();
});

function initCarSellingPlatform() {
    // Set up event listeners and initialize components
    setupModalHandlers();
    setupFormValidations();
    setupSearchFilters();
    setupImageGallery();
    setupSmoothScrolling();

    // Check for URL hash (for deep linking to sections)
    checkInitialHash();
}

// ======================
// MODAL FUNCTIONALITY
// ======================

function setupModalHandlers() {
    // Car Details Modal
    const carDetailsModal = document.getElementById('carDetailsModal');

    // Close modal when clicking the X button
    if (carDetailsModal) {
        const closeModalBtn = carDetailsModal.querySelector('.close-modal');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', closeCarDetailsModal);
        }

        // Close modal when clicking outside content
        carDetailsModal.addEventListener('click', function(e) {
            if (e.target === carDetailsModal) {
                closeCarDetailsModal();
            }
        });
    }

    // Escape key closes modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && carDetailsModal.style.display === 'block') {
            closeCarDetailsModal();
        }
    });
}

function showCarDetails(carId) {
    // Show loading state
    const modalContent = document.getElementById('modalCarContent');
    modalContent.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Loading car details...</div>';

    // Display modal
    document.getElementById('carDetailsModal').style.display = 'block';
    document.body.style.overflow = 'hidden';

    // Fetch car details
    fetch(`/cars/${carId}/detail/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load car details');
            }
            return response.text();
        })
        .then(html => {
            modalContent.innerHTML = html;

            // Initialize any interactive elements in the modal
            initModalInteractiveElements();
        })
        .catch(error => {
            console.error('Error loading car details:', error);
            modalContent.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load car details. Please try again later.</p>
                    <button onclick="showCarDetails(${carId})">Retry</button>
                </div>
            `;
        });
}

function closeCarDetailsModal() {
    const modal = document.getElementById('carDetailsModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';

    // Clear modal content to save memory
    document.getElementById('modalCarContent').innerHTML = '';
}

function initModalInteractiveElements() {
    // Initialize any interactive elements within the modal
    setupImageGallery();
    setupPurchaseButton();
}

// ======================
// IMAGE GALLERY
// ======================

function setupImageGallery() {
    // Main image switching for thumbnails
    document.querySelectorAll('.thumbnail-images img').forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            const mainImage = document.getElementById('mainCarImage');
            if (mainImage) {
                // Add fade-out effect
                mainImage.style.opacity = 0;

                // After fade out completes, change image and fade in
                setTimeout(() => {
                    mainImage.src = this.src;
                    mainImage.style.opacity = 1;
                }, 200);
            }
        });

        // Add hover effect
        thumbnail.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'transform 0.2s ease';
        });

        thumbnail.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// ======================
// PURCHASE FUNCTIONALITY
// ======================

function setupPurchaseButton() {
    const purchaseBtn = document.querySelector('.purchase-btn');
    if (purchaseBtn) {
        purchaseBtn.addEventListener('click', function() {
            const carId = this.getAttribute('data-car-id') ||
                         this.closest('[data-car-id]').getAttribute('data-car-id');
            openPurchaseForm(carId);
        });
    }
}

function openPurchaseForm(carId) {
    // Close the details modal first
    closeCarDetailsModal();

    // Smooth scroll to top then navigate
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });

    // Small delay for better UX
    setTimeout(() => {
        window.location.href = `/cars/${carId}/purchase/`;
    }, 300);
}

// ======================
// FORM VALIDATIONS
// ======================

function setupFormValidations() {
    // Sell Car Form Validation
    const sellCarForm = document.querySelector('.sell-car-form form');
    if (sellCarForm) {
        sellCarForm.addEventListener('submit', function(e) {
            if (!validateSellCarForm(this)) {
                e.preventDefault();
                return false;
            }
            return true;
        });
    }

    // Purchase Form Validation
    const purchaseForm = document.querySelector('.purchase-form form');
    if (purchaseForm) {
        purchaseForm.addEventListener('submit', function(e) {
            if (!validatePurchaseForm(this)) {
                e.preventDefault();
                return false;
            }
            return true;
        });
    }
}

function validateSellCarForm(form) {
    let isValid = true;
    const priceInput = form.querySelector('input[name="price"]');
    const mileageInput = form.querySelector('input[name="mileage"]');
    const engineInput = form.querySelector('input[name="engine_capacity"]');
    const imagesInput = form.querySelector('input[name="images"]');

    // Validate price
    if (parseFloat(priceInput.value) <= 0) {
        showInputError(priceInput, 'Price must be greater than 0');
        isValid = false;
    } else {
        clearInputError(priceInput);
    }

    // Validate mileage
    if (parseInt(mileageInput.value) <= 0) {
        showInputError(mileageInput, 'Mileage must be greater than 0');
        isValid = false;
    } else {
        clearInputError(mileageInput);
    }

    // Validate engine capacity
    if (parseInt(engineInput.value) <= 0) {
        showInputError(engineInput, 'Engine capacity must be greater than 0');
        isValid = false;
    } else {
        clearInputError(engineInput);
    }

    // Validate at least one image is uploaded
    if (imagesInput && imagesInput.files.length === 0) {
        showInputError(imagesInput, 'Please upload at least one image of your car');
        isValid = false;
    } else if (imagesInput) {
        clearInputError(imagesInput);
    }

    return isValid;
}

function validatePurchaseForm(form) {
    let isValid = true;
    const offerInput = form.querySelector('input[name="offer_price"]');
    const messageInput = form.querySelector('textarea[name="message"]');

    // Validate offer price
    if (parseFloat(offerInput.value) <= 0) {
        showInputError(offerInput, 'Offer price must be greater than 0');
        isValid = false;
    } else {
        clearInputError(offerInput);
    }

    // Validate message length
    if (messageInput.value.trim().length < 10) {
        showInputError(messageInput, 'Please write a more detailed message (at least 10 characters)');
        isValid = false;
    } else {
        clearInputError(messageInput);
    }

    return isValid;
}

function showInputError(inputElement, message) {
    // Remove any existing error messages
    clearInputError(inputElement);

    // Add error class to input
    inputElement.classList.add('error-input');

    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;

    // Insert after input
    inputElement.parentNode.insertBefore(errorElement, inputElement.nextSibling);

    // Scroll to the first error if there are multiple
    if (!window.scrolledToError) {
        inputElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        window.scrolledToError = true;
    }
}

function clearInputError(inputElement) {
    // Remove error class
    inputElement.classList.remove('error-input');

    // Remove error message if it exists
    const errorElement = inputElement.nextElementSibling;
    if (errorElement && errorElement.classList.contains('error-message')) {
        errorElement.remove();
    }
}

// ======================
// SEARCH & FILTERS
// ======================

function setupSearchFilters() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        // Debounce the search to prevent too many requests
        const debouncedSearch = debounce(function() {
            searchForm.submit();
        }, 500);

        // Listen for changes in search inputs
        searchForm.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', debouncedSearch);
        });

        // For select elements, submit immediately on change
        searchForm.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', function() {
                searchForm.submit();
            });
        });
    }
}

// ======================
// UTILITY FUNCTIONS
// ======================

function setupSmoothScrolling() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });

                // Update URL hash without jumping
                if (history.pushState) {
                    history.pushState(null, null, targetId);
                } else {
                    location.hash = targetId;
                }
            }
        });
    });
}

function checkInitialHash() {
    // Check if URL has a hash and scroll to it
    if (window.location.hash) {
        const targetElement = document.querySelector(window.location.hash);
        if (targetElement) {
            setTimeout(() => {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }, 100);
        }
    }
}

function debounce(func, wait) {
    // Debounce function to limit how often a function can fire
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

// ======================
// CARD INTERACTIONS
// ======================

// Add hover effects to car cards
document.querySelectorAll('.car-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
        this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.2)';

        // Scale up the image slightly
        const img = this.querySelector('.car-image img');
        if (img) {
            img.style.transform = 'scale(1.05)';
        }
    });

    card.addEventListener('mouseleave', function() {
        this.style.transform = '';
        this.style.boxShadow = '';

        // Reset image scale
        const img = this.querySelector('.car-image img');
        if (img) {
            img.style.transform = '';
        }
    });

    // Click handler is already set in HTML with onclick="showCarDetails()"
});

// ======================
// ERROR HANDLING
// ======================

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Unhandled error:', e.error);

    // You could show a user-friendly error message here
    // const errorDisplay = document.getElementById('global-error-display');
    // if (errorDisplay) {
    //     errorDisplay.textContent = 'An unexpected error occurred. Please try again.';
    //     errorDisplay.style.display = 'block';
    // }
});

// Handle failed fetch requests
window.addEventListener('unhandledrejection', event => {
    console.error('Unhandled promise rejection:', event.reason);
    // Optionally show error to user
});
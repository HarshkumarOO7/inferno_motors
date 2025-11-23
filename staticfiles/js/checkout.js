document.addEventListener('DOMContentLoaded', function() {
    const confirmOrderBtn = document.getElementById('confirm-order');
    const orderConfirmation = document.getElementById('orderConfirmation');
    const continueShoppingBtn = document.getElementById('continueShopping');
    const addressForm = document.getElementById('addressForm');

    confirmOrderBtn.addEventListener('click', function() {
        // Validate form
        if (!addressForm.checkValidity()) {
            addressForm.reportValidity();
            return;
        }

        if (!document.getElementById('payment-confirm').checked) {
            alert('Please confirm that you have completed the payment');
            return;
        }

        // Collect form data
        const formData = new FormData(addressForm);

        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Send data to server
        fetch(CONFIRM_ORDER_URL, {  // Use the variable we defined in the template
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Show confirmation popup
                orderConfirmation.style.display = 'flex';
            } else {
                alert(data.error || 'There was an error processing your order. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error processing your order. Please try again.');
        });
    });

    // Continue Shopping Button
    continueShoppingBtn.addEventListener('click', function() {
        window.location.href = HOME_URL;  // Use the variable we defined in the template
    });

    // Payment Option Selection
    const paymentOptions = document.querySelectorAll('.payment-option');
    paymentOptions.forEach(option => {
        option.addEventListener('click', function() {
            paymentOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
        });
    });
});


document.addEventListener('DOMContentLoaded', function() {
    // Get all elements
    const quantityInput = document.getElementById('quantity');
    const decreaseBtn = document.getElementById('decrease-qty');
    const increaseBtn = document.getElementById('increase-qty');
    const totalPrice = document.getElementById('total-price');
    const qrCodeImage = document.getElementById('qr-code-image');
    const hiddenQuantity = document.getElementById('hidden-quantity');

    // Debug: Verify values are being received correctly
    console.log("Unit Price:", UNIT_PRICE);
    console.log("Max Quantity:", MAX_QUANTITY);
    console.log("Initial Quantity:", INITIAL_QUANTITY);

    // Initialize quantity input
    quantityInput.value = INITIAL_QUANTITY;

    // Update all price-related elements
    function updatePrices() {
        const currentQuantity = parseInt(quantityInput.value);
        const newTotal = (UNIT_PRICE * currentQuantity).toFixed(2);

        // Update displayed values
        totalPrice.textContent = newTotal;
        hiddenQuantity.value = currentQuantity;

        // Update QR code
        if (qrCodeImage) {
            qrCodeImage.src = `${QR_CODE_URL}?price=${newTotal}`;
        }

        // Update other price displays
        document.getElementById('qr-amount').textContent = newTotal;
        document.getElementById('payment-amount').textContent = newTotal;
    }

    // Decrease quantity
    decreaseBtn.addEventListener('click', function(e) {
        e.preventDefault();
        let currentQty = parseInt(quantityInput.value);
        if (currentQty > 1) {
            quantityInput.value = currentQty - 1;
            updatePrices();
        }
    });

    // Increase quantity
    increaseBtn.addEventListener('click', function(e) {
        e.preventDefault();
        let currentQty = parseInt(quantityInput.value);
        if (currentQty < MAX_QUANTITY) {
            quantityInput.value = currentQty + 1;
            updatePrices();
        } else {
            alert(`Only ${MAX_QUANTITY} units available in stock.`);
        }
    });

    // Initialize prices on page load
    updatePrices();

    // Rest of your existing code...
});
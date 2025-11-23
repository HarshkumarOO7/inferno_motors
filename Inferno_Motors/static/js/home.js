// Glowing effect for logo on scroll
window.addEventListener('scroll', function () {
    const logo = document.querySelector('.logo');
    if (window.scrollY > 50) {
        logo.style.textShadow = '0 0 10px rgba(243, 156, 18, 0.8)';
    } else {
        logo.style.textShadow = 'none';
    }
});

// Hero section text typing effect
const heroText = document.querySelector('.hero h1');
const text = heroText.textContent;
heroText.textContent = '';
let i = 0;

function typeWriter() {
    if (i < text.length) {
        heroText.textContent += text.charAt(i);
        i++;
        setTimeout(typeWriter, 100);
    }
}

document.addEventListener('DOMContentLoaded', typeWriter);

// Smooth scroll to anchor links
const anchorLinks = document.querySelectorAll('a[href^="#"]');
anchorLinks.forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        target.scrollIntoView({ behavior: 'smooth' });
    });
});

// Background scroll effect
window.addEventListener('scroll', function () {
    const scrollY = window.scrollY;
    document.body.style.backgroundPositionY = `-${scrollY * 0.5}px`;
});

document.getElementById('searchParts').addEventListener('click', function () {
    const companyName = document.getElementById('companyName').value;
    const carModel = document.getElementById('carModel').value;
    const carPart = document.getElementById('carPart').value;

    if (companyName && carModel && carPart) {
        alert(`Searching for ${carPart} for ${companyName} ${carModel}...`);
        // You can add AJAX or fetch API calls here to handle the search
    } else {
        alert('Please select all fields to search for car parts.');
    }
});

function toggleDropdown(dropdownId) {
            let dropdown = document.getElementById(dropdownId);
            dropdown.style.display = (dropdown.style.display === "block") ? "none" : "block";
        }

        function selectCompany(id, name, image) {
            document.getElementById("company-selected").innerHTML = `<img src="${image}" alt="${name}"> ${name}`;
            document.getElementById("company-options").style.display = "none";
            loadCarModels(id);
        }

        function selectModel(id, name, image) {
            document.getElementById("model-selected").innerHTML = `<img src="${image}" alt="${name}"> ${name}`;
            document.getElementById("model-options").style.display = "none";
            loadCarParts(id);
        }

        function selectPart(id, name, image, price) {
            document.getElementById("parts-selected").innerHTML = `<img src="${image}" alt="${name}"> ${name} - $${price}`;
            document.getElementById("parts-options").style.display = "none";
        }

        function loadCarModels(companyId) {
            fetch(`/get_car_models/${companyId}/`)
                .then(response => response.json())
                .then(models => {
                    let modelDropdown = document.getElementById("model-options");
                    modelDropdown.innerHTML = '';
                    models.forEach(model => {
                        modelDropdown.innerHTML += `<div onclick="selectModel('${model.id}', '${model.name}', '${model.image}')">
                                                        <img src="${model.image}" alt="${model.name}"> ${model.name}
                                                    </div>`;
                    });
                    document.getElementById("model-section").style.display = "block";
                    document.getElementById("parts-section").style.display = "none";
                });
        }

        function loadCarParts(modelId) {
            fetch(`/get_car_parts/${modelId}/`)
                .then(response => response.json())
                .then(parts => {
                    let partsDropdown = document.getElementById("parts-options");
                    partsDropdown.innerHTML = '';
                    parts.forEach(part => {
                        partsDropdown.innerHTML += `<div onclick="selectPart('${part.id}', '${part.name}', '${part.image}', '${part.price}')">
                                                        <img src="${part.image}" alt="${part.name}"> ${part.name} - $${part.price}
                                                    </div>`;
                    });
                    document.getElementById("parts-section").style.display = "block";
                });
        }
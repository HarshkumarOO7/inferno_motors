let selectedCompany = null;
let selectedModel = null;
let selectedPart = null;

function toggleDropdown(dropdownId) {
    let dropdown = document.getElementById(dropdownId);
    dropdown.style.display = (dropdown.style.display === "block") ? "none" : "block";
}

function selectCompany(id, name, image) {
    selectedCompany = { id, name, image };
    document.getElementById("company-selected").innerHTML = `<img src="${image}" alt="${name}"> ${name}`;
    document.getElementById("company-options").style.display = "none";

    // Reset model and parts dropdowns
    resetModelAndParts();

    // Load car models for the selected company
    loadCarModels(id);
}

function selectModel(id, name, image) {
    selectedModel = { id, name, image };
    document.getElementById("model-selected").innerHTML = `<img src="${image}" alt="${name}"> ${name}`;
    document.getElementById("model-options").style.display = "none";

    // Reset parts dropdown
    resetParts();

    // Load car parts for the selected model
    loadCarParts(id);
}

function selectPart(id, name, image, price) {
    selectedPart = { id, name, image, price };
    document.getElementById("parts-selected").innerHTML = `<img src="${image}" alt="${name}"> ${name} - $${price}`;
    document.getElementById("parts-options").style.display = "none";

    // Show the Buy Now button if all selections are made
    checkSelections();
}

function resetModelAndParts() {
    selectedModel = null;
    selectedPart = null;

    document.getElementById("model-selected").innerHTML = `<span>Select Model</span><i class="fas fa-chevron-down"></i>`;
    document.getElementById("model-options").innerHTML = '';
    document.getElementById("model-section").style.display = "none";

    resetParts();
}

function resetParts() {
    selectedPart = null;

    document.getElementById("parts-selected").innerHTML = `<span>Select Part</span><i class="fas fa-chevron-down"></i>`;
    document.getElementById("parts-options").innerHTML = '';
    document.getElementById("parts-section").style.display = "none";

    // Hide the Buy Now button
    document.getElementById("buy-now-section").style.display = "none";
}

function checkSelections() {
    if (selectedCompany && selectedModel && selectedPart) {
        document.getElementById("buy-now-section").style.display = "block";
    } else {
        document.getElementById("buy-now-section").style.display = "none";
    }
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

function buyNow() {
    if (selectedCompany && selectedModel && selectedPart) {
        alert(`Thank you for purchasing!\n\nCompany: ${selectedCompany.name}\nModel: ${selectedModel.name}\nPart: ${selectedPart.name} - $${selectedPart.price}`);
    } else {
        alert("Please select a company, model, and part before purchasing.");
    }
}


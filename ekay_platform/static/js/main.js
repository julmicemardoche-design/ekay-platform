// Main JavaScript for E-KAY Platform
document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {toggle: false});
                    bsCollapse.hide();
                }
            }
        });
    });

    // Add active class to current nav link
    const currentLocation = location.href;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.href === currentLocation) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
    });

    // Property image gallery
    const propertyImages = document.querySelectorAll('.property-thumbnail');
    if (propertyImages.length > 0) {
        propertyImages.forEach(img => {
            img.addEventListener('click', function() {
                const mainImage = document.querySelector('.property-main-image');
                if (mainImage) {
                    mainImage.src = this.src;
                    
                    // Update active thumbnail
                    document.querySelector('.property-thumbnail.active').classList.remove('active');
                    this.classList.add('active');
                }
            });
        });
    }

    // Initialize image zoom
    const mainImage = document.querySelector('.property-main-image');
    if (mainImage) {
        mainImage.addEventListener('click', function() {
            this.classList.toggle('zoomed');
        });
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Price range slider
    const priceRange = document.getElementById('priceRange');
    const priceOutput = document.getElementById('priceOutput');
    if (priceRange && priceOutput) {
        priceOutput.textContent = formatPrice(priceRange.value);
        priceRange.addEventListener('input', function() {
            priceOutput.textContent = formatPrice(this.value);
        });
    }

    // Toggle password visibility
    const togglePassword = document.querySelector('.toggle-password');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const passwordInput = document.querySelector(this.getAttribute('toggle'));
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }

    // Initialize Google Maps for property location
    initMap();
});

// Format price with thousands separator
function formatPrice(price) {
    return new Intl.NumberFormat('fr-HT', {
        style: 'currency',
        currency: 'HTG',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(price).replace('HTG', 'HTG ');
}

// Initialize Google Maps
function initMap() {
    const mapElement = document.getElementById('propertyMap');
    if (!mapElement) return;
    
    // Get coordinates from data attributes or use default
    const lat = parseFloat(mapElement.dataset.lat) || 18.5944;  // Default to Port-au-Prince
    const lng = parseFloat(mapElement.dataset.lng) || -72.3074;
    
    const location = { lat: lat, lng: lng };
    
    const map = new google.maps.Map(mapElement, {
        zoom: 15,
        center: location,
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
            }
        ]
    });
    
    new google.maps.Marker({
        position: location,
        map: map,
        title: 'Property Location'
    });
}

// Handle image upload preview
function previewImage(input) {
    const preview = document.getElementById('imagePreview');
    preview.innerHTML = '';
    
    if (input.files) {
        const files = Array.from(input.files);
        
        // Limit to 10 images
        if (files.length > 10) {
            alert('Vous ne pouvez télécharger que 10 images maximum.');
            input.value = '';
            return;
        }
        
        files.forEach((file, index) => {
            if (!file.type.match('image.*')) {
                return;
            }
            
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const div = document.createElement('div');
                div.className = 'image-preview-item';
                
                const img = document.createElement('img');
                img.src = e.target.result;
                
                const removeBtn = document.createElement('div');
                removeBtn.className = 'remove-image';
                removeBtn.innerHTML = '&times;';
                removeBtn.onclick = function() {
                    div.remove();
                    // Remove the file from the file input
                    const dt = new DataTransfer();
                    const input = document.getElementById('propertyImages');
                    const { files } = input;
                    
                    for (let i = 0; i < files.length; i++) {
                        if (index !== i) {
                            dt.items.add(files[i]);
                        }
                    }
                    
                    input.files = dt.files;
                };
                
                div.appendChild(img);
                div.appendChild(removeBtn);
                preview.appendChild(div);
            };
            
            reader.readAsDataURL(file);
        });
    }
}

// Handle property search form submission
function handleSearchFormSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const params = new URLSearchParams();
    
    // Add form data to URL parameters
    for (const [key, value] of formData.entries()) {
        if (value) {
            params.append(key, value);
        }
    }
    
    // Update URL with search parameters
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);
    
    // Here you would typically make an AJAX request to fetch filtered properties
    // For now, we'll just reload the page
    window.location.href = newUrl;
}

// Add event listener to search form
const searchForm = document.getElementById('propertySearchForm');
if (searchForm) {
    searchForm.addEventListener('submit', handleSearchFormSubmit);
}

// Handle property contact form submission
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(this);
        const formObject = {};
        formData.forEach((value, key) => {
            formObject[key] = value;
        });
        
        // Here you would typically send the form data to your backend
        console.log('Form submitted:', formObject);
        
        // Show success message
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success mt-3';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            Votre message a été envoyé avec succès. Le propriétaire vous contactera bientôt.
        `;
        
        const formContainer = document.querySelector('.contact-form-container');
        formContainer.insertBefore(alertDiv, contactForm);
        
        // Reset form
        contactForm.reset();
        
        // Remove success message after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    });
}

// Add to favorites functionality
const favoriteButtons = document.querySelectorAll('.favorite-btn');
favoriteButtons.forEach(button => {
    button.addEventListener('click', function() {
        const propertyId = this.dataset.propertyId;
        const isFavorite = this.classList.contains('active');
        
        // Toggle favorite state
        this.classList.toggle('active');
        
        // Update icon
        const icon = this.querySelector('i');
        if (isFavorite) {
            icon.classList.remove('fas');
            icon.classList.add('far');
        } else {
            icon.classList.remove('far');
            icon.classList.add('fas');
        }
        
        // Here you would typically make an AJAX request to update favorites on the server
        console.log(`Property ${propertyId} ${isFavorite ? 'removed from' : 'added to'} favorites`);
        
        // Show toast notification
        const toastEl = document.getElementById('toastNotification');
        if (toastEl) {
            const toast = new bootstrap.Toast(toastEl);
            const toastBody = toastEl.querySelector('.toast-body');
            toastBody.textContent = isFavorite 
                ? 'Bien retiré de vos favoris' 
                : 'Bien ajouté à vos favoris';
            toast.show();
        }
    });
});

// Handle property availability toggle
const availabilityToggles = document.querySelectorAll('.availability-toggle');
availabilityToggles.forEach(toggle => {
    toggle.addEventListener('change', function() {
        const propertyId = this.dataset.propertyId;
        const isAvailable = this.checked;
        
        // Here you would typically make an AJAX request to update availability on the server
        console.log(`Property ${propertyId} availability set to: ${isAvailable ? 'available' : 'unavailable'}`);
        
        // Show toast notification
        const toastEl = document.getElementById('toastNotification');
        if (toastEl) {
            const toast = new bootstrap.Toast(toastEl);
            const toastBody = toastEl.querySelector('.toast-body');
            toastBody.textContent = isAvailable 
                ? 'Le bien est maintenant marqué comme disponible' 
                : 'Le bien est maintenant marqué comme indisponible';
            toast.show();
        }
    });
});

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation du carrousel de témoignages
    initTestimonialCarousel();
    
    // Initialisation du compteur de statistiques
    initStatsCounter();
    
    // Gestion du formulaire de recherche
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }
    
    // Gestion du défilement fluide pour les ancres
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Animation au défilement
    initScrollAnimations();
});

/**
 * Initialise le carrousel de témoignages
 */
function initTestimonialCarousel() {
    const testimonialCarousel = document.querySelector('#testimonialCarousel');
    if (!testimonialCarousel) return;
    
    // Utiliser le carrousel Bootstrap si disponible
    if (typeof bootstrap !== 'undefined' && bootstrap.Carousel) {
        new bootstrap.Carousel(testimonialCarousel, {
            interval: 10000,
            touch: true
        });
    }
    
    // Navigation personnalisée
    const prevBtn = document.querySelector('.testimonial-prev');
    const nextBtn = document.querySelector('.testimonial-next');
    
    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', function() {
            const carousel = bootstrap.Carousel.getInstance(testimonialCarousel);
            carousel.prev();
        });
        
        nextBtn.addEventListener('click', function() {
            const carousel = bootstrap.Carousel.getInstance(testimonialCarousel);
            carousel.next();
        });
    }
}

/**
 * Initialise l'animation des compteurs de statistiques
 */
function initStatsCounter() {
    const statElements = document.querySelectorAll('.stat-number');
    if (statElements.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const targetValue = parseInt(target.getAttribute('data-target'));
                const duration = 2000; // 2 secondes
                const step = (targetValue / duration) * 10;
                
                let current = 0;
                const timer = setInterval(() => {
                    current += step;
                    if (current >= targetValue) {
                        current = targetValue;
                        clearInterval(timer);
                    }
                    target.textContent = Math.floor(current);
                }, 10);
                
                // Ne plus observer après l'animation
                observer.unobserve(target);
            }
        });
    }, { threshold: 0.5 });
    
    statElements.forEach(stat => {
        stat.setAttribute('data-target', stat.textContent);
        stat.textContent = '0';
        observer.observe(stat);
    });
}

/**
 * Gère la soumission du formulaire de recherche
 */
function handleSearchSubmit(e) {
    e.preventDefault();
    
    // Récupérer les valeurs du formulaire
    const formData = new FormData(this);
    const searchParams = new URLSearchParams();
    
    // Ajouter les paramètres de recherche
    formData.forEach((value, key) => {
        if (value) {
            searchParams.append(key, value);
        }
    });
    
    // Rediriger vers la page de résultats de recherche
    window.location.href = `/properties/search?${searchParams.toString()}`;
}

/**
 * Initialise les animations au défilement
 */
function initScrollAnimations() {
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    if (animateElements.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                // Ne plus observer après l'animation
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    animateElements.forEach(element => {
        observer.observe(element);
    });
}

/**
 * Affiche un message de notification
 * @param {string} message - Le message à afficher
 * @param {string} type - Le type de message (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    const container = document.createElement('div');
    container.className = `notification ${type}`;
    container.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    document.body.appendChild(container);
    
    // Fermer la notification au clic sur le bouton
    const closeBtn = container.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        container.classList.add('fade-out');
        setTimeout(() => {
            container.remove();
        }, 300);
    });
    
    // Fermer automatiquement après 5 secondes
    setTimeout(() => {
        if (container.parentNode) {
            container.classList.add('fade-out');
            setTimeout(() => {
                container.remove();
            }, 300);
        }
    }, 5000);
}

// Exposer les fonctions au scope global
window.showNotification = showNotification;

/**
 * Gestion des notifications et des états de chargement
 * Ce script fournit des fonctions pour afficher des notifications toast
 * et gérer l'affichage d'un écran de chargement
 */

// Conteneur pour les notifications
document.addEventListener('DOMContentLoaded', function() {
    // Créer le conteneur des notifications s'il n'existe pas
    if (!document.querySelector('.toast-container')) {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
    }
});

/**
 * Affiche une notification à l'utilisateur
 * @param {string} message - Le message à afficher
 * @param {string} type - Le type de notification (info, success, danger, warning)
 */
function showAlert(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast show`;
    toast.role = 'alert';
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    // Déterminer l'icône et le titre en fonction du type de message
    let icon, title, bgClass;
    switch(type) {
        case 'success':
            icon = 'check-circle';
            title = 'Succès';
            bgClass = 'bg-success text-white';
            break;
        case 'danger':
            icon = 'exclamation-circle';
            title = 'Erreur';
            bgClass = 'bg-danger text-white';
            break;
        case 'warning':
            icon = 'exclamation-triangle';
            title = 'Avertissement';
            bgClass = 'bg-warning text-dark';
            break;
        default:
            icon = 'info-circle';
            title = 'Information';
            bgClass = 'bg-info text-white';
    }

    // Créer la structure HTML de la notification
    toast.innerHTML = `
        <div class="toast-header ${bgClass}">
            <i class="fas fa-${icon} me-2"></i>
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Fermer"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    // Ajouter la notification au conteneur
    toastContainer.appendChild(toast);

    // Initialiser le composant toast de Bootstrap
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();

    // Supprimer la notification du DOM après sa fermeture
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Affiche ou masque l'écran de chargement
 * @param {boolean} show - Afficher ou masquer l'écran de chargement
 * @param {string} message - Message optionnel à afficher
 */
function setLoading(show, message = 'Chargement en cours...') {
    let overlay = document.getElementById('loading-overlay');
    
    // Créer l'overlay s'il n'existe pas
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="mt-2">${message}</p>
        `;
        document.body.appendChild(overlay);
        
        // Ajouter les styles CSS si nécessaire
        if (!document.getElementById('loading-overlay-styles')) {
            const style = document.createElement('style');
            style.id = 'loading-overlay-styles';
            style.textContent = `
                .loading-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(255, 255, 255, 0.9);
                    display: none;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                    z-index: 9999;
                    backdrop-filter: blur(2px);
                }
                .toast {
                    min-width: 300px;
                    margin-bottom: 1rem;
                }
                .toast.show {
                    opacity: 1;
                }
            `;
            document.head.appendChild(style);
        }
    } else {
        // Mettre à jour le message si fourni
        const messageElement = overlay.querySelector('p');
        if (messageElement) {
            messageElement.textContent = message;
        }
    }

    // Afficher ou masquer l'overlay
    overlay.style.display = show ? 'flex' : 'none';
}

// Intercepter les soumissions de formulaire pour afficher le chargement
document.addEventListener('submit', function(e) {
    const form = e.target;
    
    // Vérifier si le formulaire doit déclencher le chargement
    if (form.hasAttribute('data-ajax-loading') || form.classList.contains('needs-validation')) {
        setLoading(true, 'Traitement en cours...');
        
        // Si c'est une soumission AJAX, ne pas empêcher le comportement par défaut
        if (form.hasAttribute('data-ajax')) {
            return;
        }
        
        // Pour les formulaires normaux, laisser la soumission se faire normalement
        // après un court délai pour permettre à l'overlay de s'afficher
        e.preventDefault();
        setTimeout(() => {
            form.submit();
        }, 100);
    }
});

// Exposer les fonctions globalement
window.showAlert = showAlert;
window.setLoading = setLoading;

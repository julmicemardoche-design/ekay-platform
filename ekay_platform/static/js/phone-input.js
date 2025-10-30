// Import des données des pays (chargées séparément)
let phoneCountries = [];

// Fonction pour initialiser le sélecteur de pays
function initPhoneInput(phoneInputId = 'phone', countrySelectId = 'phone_country') {
    const phoneInput = document.getElementById(phoneInputId);
    const countrySelect = document.getElementById(countrySelectId);
    
    if (!phoneInput || !countrySelect) return;
    
    // Charger les données des pays
    fetch('/static/js/phone-codes.js')
        .then(response => response.text())
        .then(scriptText => {
            // Extraire le tableau des pays du script
            const match = scriptText.match(/export const phoneCountries = (\[.*?\]);/s);
            if (match && match[1]) {
                phoneCountries = JSON.parse(match[1].replace(/\n/g, '').replace(/\s+/g, ' '));
                updateCountrySelect();
            }
        })
        .catch(error => console.error('Erreur lors du chargement des données de pays:', error));
    
    // Mettre à jour le sélecteur de pays
    function updateCountrySelect() {
        if (!phoneCountries.length) return;
        
        // Trier les pays par nom
        const sortedCountries = [...phoneCountries].sort((a, b) => a.name.localeCompare(b.name));
        
        // Vider et remplir le sélecteur
        countrySelect.innerHTML = '';
        
        // Ajouter l'option par défaut (Haïti)
        const defaultCountry = phoneCountries.find(c => c.code === 'HT') || phoneCountries[0];
        const defaultOption = document.createElement('option');
        defaultOption.value = defaultCountry.code;
        defaultOption.setAttribute('data-prefix', defaultCountry.prefix);
        defaultOption.textContent = `${defaultCountry.flag} ${defaultCountry.name} (${defaultCountry.prefix})`;
        defaultOption.selected = true;
        countrySelect.appendChild(defaultOption);
        
        // Ajouter les autres pays
        sortedCountries.forEach(country => {
            if (country.code !== defaultCountry.code) {
                const option = document.createElement('option');
                option.value = country.code;
                option.setAttribute('data-prefix', country.prefix);
                option.textContent = `${country.flag} ${country.name} (${country.prefix})`;
                countrySelect.appendChild(option);
            }
        });
        
        // Mettre à jour le préfixe lorsque le pays change
        countrySelect.addEventListener('change', updatePhonePrefix);
        
        // Formater le numéro de téléphone
        phoneInput.addEventListener('input', formatPhoneNumber);
    }
    
    // Mettre à jour le préfixe du numéro de téléphone
    function updatePhonePrefix() {
        const selectedOption = countrySelect.options[countrySelect.selectedIndex];
        const prefix = selectedOption.getAttribute('data-prefix');
        
        // Mettre à jour le champ caché du préfixe s'il existe
        const prefixInput = document.getElementById('phone_prefix');
        if (prefixInput) {
            prefixInput.value = prefix;
        }
        
        // Mettre à jour le préfixe dans le champ de téléphone
        let currentValue = phoneInput.value.trim();
        
        // Supprimer l'ancien préfixe s'il existe
        phoneCountries.forEach(country => {
            if (currentValue.startsWith(country.prefix)) {
                currentValue = currentValue.substring(country.prefix.length).trim();
            }
        });
        
        // Ajouter le nouveau préfixe
        phoneInput.value = `${prefix} ${currentValue}`;
    }
    
    // Formater le numéro de téléphone lors de la saisie
    function formatPhoneNumber() {
        let value = phoneInput.value.replace(/\D/g, ''); // Supprimer tous les caractères non numériques
        const selectedOption = countrySelect.options[countrySelect.selectedIndex];
        const prefix = selectedOption.getAttribute('data-prefix').replace(/\D/g, ''); // Préfixe sans les caractères non numériques
        
        // Si la valeur commence par le préfixe, le supprimer pour le reformater
        if (value.startsWith(prefix)) {
            value = value.substring(prefix.length);
        }
        
        // Limiter la longueur du numéro (15 chiffres max)
        if (value.length > 15) {
            value = value.substring(0, 15);
        }
        
        // Formater le numéro avec des espaces pour une meilleure lisibilité
        let formattedValue = '';
        for (let i = 0; i < value.length; i++) {
            if (i > 0 && i % 2 === 0) {
                formattedValue += ' ';
            }
            formattedValue += value[i];
        }
        
        // Mettre à jour la valeur avec le préfixe et le numéro formaté
        phoneInput.value = `${selectedOption.getAttribute('data-prefix')} ${formattedValue}`.trim();
    }
    
    // Initialiser le préfixe
    updatePhonePrefix();
}

// Initialiser automatiquement les champs de téléphone au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initPhoneInput();
});

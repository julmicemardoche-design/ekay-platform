// Configuration de la carte
function initPropertyMap() {
    // Récupération des données depuis les attributs data-
    const mapElement = document.getElementById('property-map');
    if (!mapElement) return;
    
    const defaultLat = parseFloat(mapElement.dataset.lat) || 19.6917;
    const defaultLng = parseFloat(mapElement.dataset.lng) || -71.8250;
    const villageName = mapElement.dataset.village || 'La Différence';
    const propertyTitle = mapElement.dataset.title || 'Propriété';
    
    // Création de la carte
    const map = L.map('property-map').setView([defaultLat, defaultLng], 15);
    
    // Ajout de la couche OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Ajout d'un marqueur pour la propriété
    L.marker([defaultLat, defaultLng])
        .addTo(map)
        .bindPopup(`<b>${propertyTitle}</b><br>${villageName}, Caracol, Haïti`)
        .openPopup();
    
    // Optionnel: Ajout d'un cercle pour représenter la zone du village
    L.circle([defaultLat, defaultLng], {
        color: '#3388ff',
        fillColor: '#3388ff',
        fillOpacity: 0.1,
        radius: 500 // Rayon en mètres
    }).addTo(map);
}

// Initialisation de la carte quand le DOM est chargé
document.addEventListener('DOMContentLoaded', initPropertyMap);

import pytest
from flask import url_for, get_flashed_messages
from ekay_platform.models import Property

def test_index(client):
    """Test de la page d'accueil des propriétés"""
    response = client.get('/properties/')
    assert response.status_code == 200
    # Vérifier que la page contient le titre (qui est défini dans le template de base)
    assert b'<h1' in response.data

def test_new_property_requires_login(client):
    """Test que la création d'une propriété nécessite une connexion"""
    response = client.get('/properties/new', follow_redirects=True)
    assert b'Please log in to access this page' in response.data

def test_new_property_form_display(client, auth):
    """Test que le formulaire de création s'affiche correctement"""
    # Se connecter
    auth.login()
    
    # Accéder au formulaire
    response = client.get('/properties/new')
    assert response.status_code == 200
    
    # Vérifier que les champs obligatoires sont présents
    assert b'name="title"' in response.data
    assert b'name="description"' in response
    assert b'name="property_type"' in response.data
    assert b'name="transaction_type"' in response.data
    assert b'name="price"' in response.data
    assert b'name="address"' in response.data

def test_create_property_valid(client, auth):
    """Test de création d'une propriété avec des données valides"""
    # Se connecter
    auth.login()
    
    # Données de test
    data = {
        'title': 'Belle maison de campagne',
        'description': 'Une magnifique maison avec jardin',
        'property_type': 'house',
        'transaction_type': 'sale',
        'price': '250000',
        'address': '123 Rue de la Paix',
        'city': 'Paris',
        'country': 'France',
        'rooms': '4',
        'bedrooms': '3',
        'bathrooms': '2',
        'contact_name': 'John Doe',
        'contact_email': 'john@example.com',
        'contact_phone': '0123456789',
        'submit': 'Publier l\'annonce'
    }
    
    # Soumettre le formulaire
    response = client.post('/properties/new', data=data, follow_redirects=True)
    
    # Vérifier la redirection
    assert response.status_code == 200
    
    # Vérifier le message flash
    assert b'Votre annonce a \xc3\xa9t\xc3\xa9 publi\xc3\xa9e avec succ\xc3\xa8s' in response.data
    
    # Vérifier que la propriété a été créée en base de données
    with client.application.app_context():
        property = Property.query.first()
        assert property is not None
        assert property.title == 'Belle maison de campagne'
        assert property.status == 'published'

# Ajoutez d'autres tests ici...

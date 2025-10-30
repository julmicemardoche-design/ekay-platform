from app import app, db, User, Property, PropertyImage
from werkzeug.security import generate_password_hash
import os

def create_test_data():
    with app.app_context():
        # Supprimer les données existantes
        db.drop_all()
        db.create_all()
        
        # Créer un administrateur
        admin = User(
            username='admin',
            email='admin@ekam.com',
            password_hash=generate_password_hash('admin123'),
            phone='1234567890',
            is_admin=True
        )
        
        # Créer un propriétaire
        owner = User(
            username='proprio1',
            email='proprio@example.com',
            password_hash=generate_password_hash('proprio123'),
            phone='0987654321',
            is_landlord=True
        )
        
        # Créer un locataire
        tenant = User(
            username='locataire1',
            email='locataire@example.com',
            password_hash=generate_password_hash('loc123'),
            phone='0123456789'
        )
        
        db.session.add_all([admin, owner, tenant])
        db.session.commit()
        
        # Créer des propriétés de test
        properties = [
            {
                'title': 'Belle maison avec jardin',
                'description': 'Magnifique maison de 3 chambres avec grand jardin et vue sur la mer.',
                'price': 500,
                'annual_price': 5500,
                'rooms': 3,
                'address': '123 Rue Principale, Caracol',
                'corridor': 'A1',
                'village': 'Caracol',
                'latitude': 19.6917,
                'longitude': -71.8250,
                'user_id': owner.id
            },
            {
                'title': 'Appartement moderne centre-ville',
                'description': 'Appartement moderne de 2 chambres au cœur de la ville, proche de tous les commerces.',
                'price': 350,
                'annual_price': 3800,
                'rooms': 2,
                'address': '456 Avenue du Commerce, Caracol',
                'corridor': 'B2',
                'village': 'Caracol',
                'latitude': 19.6930,
                'longitude': -71.8230,
                'user_id': owner.id
            },
            {
                'title': 'Studio meublé étudiant',
                'description': 'Studio meublé idéal pour étudiant, proche de l\'université.',
                'price': 250,
                'annual_price': 2700,
                'rooms': 1,
                'address': '789 Rue des Écoles, Caracol',
                'corridor': 'C3',
                'village': 'Caracol',
                'latitude': 19.6900,
                'longitude': -71.8270,
                'user_id': owner.id
            }
        ]
        
        for prop_data in properties:
            prop = Property(**prop_data)
            db.session.add(prop)
            db.session.commit()
            
            # Ajouter une image par défaut à chaque propriété
            image = PropertyImage(
                filename='no-image.jpg',
                property_id=prop.id
            )
            db.session.add(image)
            
        db.session.commit()
        
        print("Données de test créées avec succès!")
        print("Compte admin: email=admin@ekam.com, mot de passe=admin123")
        print("Compte propriétaire: email=proprio@example.com, mot de passe=proprio123")
        print("Compte locataire: email=locataire@example.com, mot de passe=loc123")

if __name__ == '__main__':
    create_test_data()

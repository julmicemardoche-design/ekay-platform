from app import create_app, db
from ekay_platform.models import User, Property, PropertyImage
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def add_test_data():
    app = create_app()
    
    with app.app_context():
        # Vérifier si la table users existe
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if not inspector.has_table('users'):
            print("Création des tables...")
            db.create_all()
        
        print("Ajout des utilisateurs de test...")
        # Créer un utilisateur de test
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('test123'),
            is_landlord=True,
            created_at=datetime.now()
        )
        db.session.add(user)
        
        # Créer un administrateur
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            created_at=datetime.now()
        )
        db.session.add(admin)
        
        # Valider les utilisateurs d'abord
        db.session.commit()
        
        print("Ajout des propriétés de test...")
        # Créer des propriétés de test
        property1 = Property(
            title='Appartement moderne en centre-ville',
            description='Bel appartement lumineux avec vue sur la ville',
            price=750.0,
            rooms=3,
            address='123 Rue Principale, Ville',
            corridor='A',
            color='Bleu',
            is_available=True,
            available_from=datetime.now(),
            min_stay=12,
            user_id=user.id
        )
        db.session.add(property1)
        
        property2 = Property(
            title='Studio étudiant proche université',
            description='Studio meublé idéal pour étudiant',
            price=450.0,
            rooms=1,
            address='456 Avenue des Étudiants',
            is_available=True,
            available_from=datetime.now() + timedelta(days=30),
            min_stay=6,
            user_id=user.id
        )
        db.session.add(property2)
        
        # Valider les propriétés
        db.session.commit()
        
        print("Ajout des images des propriétés...")
        # Ajouter des images aux propriétés
        image1 = PropertyImage(
            filename='property1.jpg',
            is_primary=True,
            property_id=property1.id
        )
        db.session.add(image1)
        
        image2 = PropertyImage(
            filename='property2.jpg',
            is_primary=True,
            property_id=property2.id
        )
        db.session.add(image2)
        
        # Valider les images
        db.session.commit()
        
        print("Données de test ajoutées avec succès !")
        print(f"Utilisateur de test créé - Nom d'utilisateur: testuser, Mot de passe: test123")
        print(f"Administrateur créé - Nom d'utilisateur: admin, Mot de passe: admin123")

if __name__ == '__main__':
    add_test_data()

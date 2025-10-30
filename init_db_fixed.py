from app import create_app, db
from ekay_platform.models import User, Property, PropertyImage
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_db():
    app = create_app()
    
    with app.app_context():
        # Supprimer toutes les données existantes et créer les tables
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Créer un utilisateur de test
        print("Creating test user...")
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('test123'),
            is_landlord=True,
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        
        # Créer un administrateur
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        
        # Créer des propriétés de test
        print("Creating test properties...")
        property1 = Property(
            title='Appartement moderne en centre-ville',
            description='Bel appartement lumineux avec vue sur la ville',
            price=750.0,
            rooms=3,
            address='123 Rue Principale, Ville',
            corridor='A',
            color='Bleu',
            is_available=True,
            available_from=datetime.utcnow(),
            min_stay=12,
            owner=user
        )
        db.session.add(property1)
        
        property2 = Property(
            title='Studio étudiant proche université',
            description='Studio meublé idéal pour étudiant',
            price=450.0,
            rooms=1,
            address='456 Avenue des Étudiants',
            is_available=True,
            available_from=datetime.utcnow() + timedelta(days=30),
            min_stay=6,
            owner=user
        )
        db.session.add(property2)
        
        # Ajouter des images aux propriétés
        print("Adding property images...")
        image1 = PropertyImage(
            filename='property1.jpg',
            is_primary=True,
            property=property1
        )
        db.session.add(image1)
        
        image2 = PropertyImage(
            filename='property2.jpg',
            is_primary=True,
            property=property2
        )
        db.session.add(image2)
        
        # Valider les changements
        print("Committing changes to database...")
        db.session.commit()
        
        print("Database initialized successfully!")
        print(f"Test user created - Username: testuser, Password: test123")
        print(f"Admin user created - Username: admin, Password: admin123")

if __name__ == '__main__':
    init_db()

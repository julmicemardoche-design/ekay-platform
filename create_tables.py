from app import create_app, db
from ekay_platform.models import User, Property, PropertyImage
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_tables():
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create test user
        hashed_password = generate_password_hash('password123')
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=hashed_password,
            is_landlord=True,
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        
        # Create test properties
        properties = [
            {
                'title': 'Appartement moderne en centre-ville',
                'description': 'Bel appartement lumineux avec vue sur la ville',
                'price': 750.0,
                'rooms': 3,
                'address': '123 Rue Principale, Ville',
                'corridor': 'A',
                'color': 'Bleu',
                'is_available': True,
                'available_from': datetime.utcnow(),
                'min_stay': 12
            },
            {
                'title': 'Studio étudiant proche université',
                'description': 'Studio meublé idéal pour étudiant',
                'price': 450.0,
                'rooms': 1,
                'address': '456 Avenue des Étudiants',
                'is_available': True,
                'available_from': datetime.utcnow() + timedelta(days=30),
                'min_stay': 6
            }
        ]
        
        for prop_data in properties:
            prop = Property(**prop_data, user_id=user.id)
            db.session.add(prop)
            
            # Add a sample image for each property
            image = PropertyImage(
                filename=f"property_{prop.id}.jpg",
                is_primary=True,
                property=prop
            )
            db.session.add(image)
        
        # Commit all changes
        db.session.commit()
        print("Database initialized with test data!")

if __name__ == '__main__':
    create_tables()

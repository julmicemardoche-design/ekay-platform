from app import app, db, User, Property, PropertyImage
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Supprimer toutes les tables existantes
        db.drop_all()
        
        # Créer toutes les tables
        db.create_all()
        
        # Créer un utilisateur admin
        admin = User(
            username='admin',
            email='admin@ekam.com',
            password_hash=generate_password_hash('admin123'),
            phone='1234567890',
            is_landlord=True,
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("Base de données initialisée avec succès!")
        print(f"Utilisateur admin créé avec l'email: admin@ekam.com et le mot de passe: admin123")

if __name__ == '__main__':
    init_db()

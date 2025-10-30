"""
Script pour initialiser la base de données E-KAY avec les tables nécessaires.
"""
import os
import sys
from datetime import datetime, timedelta

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from ekay_platform.models import User, Property, PropertyImage
from werkzeug.security import generate_password_hash

def init_db():
    # Créer l'application Flask
    app = create_app()
    
    with app.app_context():
        try:
            # Supprimer toutes les tables existantes
            print("Suppression des tables existantes...")
            db.drop_all()
            
            # Créer toutes les tables
            print("Création des tables...")
            db.create_all()
            
            # Vérifier que les tables ont été créées
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("ERREUR : Aucune table n'a été créée. Vérifiez les modèles et la configuration de la base de données.")
                return False
                
            print("\nTables créées avec succès :")
            for table in tables:
                print(f"- {table}")
            
            # Créer un utilisateur de test
            print("\nCréation de l'utilisateur de test...")
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('test123'),
                is_landlord=True,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            
            # Créer un administrateur
            print("Création de l'administrateur...")
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                created_at=datetime.utcnow()
            )
            db.session.add(admin)
            
            # Valider les utilisateurs
            db.session.commit()
            
            # Créer des propriétés de test
            print("\nCréation des propriétés de test...")
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
                available_from=datetime.utcnow() + timedelta(days=30),
                min_stay=6,
                user_id=user.id
            )
            db.session.add(property2)
            
            # Valider les propriétés
            db.session.commit()
            
            # Ajouter des images aux propriétés
            print("\nAjout des images des propriétés...")
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
            
            print("\nBase de données initialisée avec succès !")
            print(f"\nUtilisateur de test créé :")
            print(f"- Nom d'utilisateur: testuser")
            print(f"- Mot de passe: test123")
            print(f"- Email: test@example.com")
            
            print(f"\nAdministrateur créé :")
            print(f"- Nom d'utilisateur: admin")
            print(f"- Mot de passe: admin123")
            print(f"- Email: admin@example.com")
            
            return True
            
        except Exception as e:
            import traceback
            print(f"\nERREUR lors de l'initialisation de la base de données : {e}")
            print("\nDétails de l'erreur :")
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=== Initialisation de la base de données E-KAY ===\n")
    if init_db():
        print("\n=== Initialisation terminée avec succès ===")
    else:
        print("\n=== Échec de l'initialisation de la base de données ===")

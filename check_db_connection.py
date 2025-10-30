"""
Script pour vérifier la connexion à la base de données et les tables.
"""
import os
import sys
from sqlalchemy import create_engine, inspect

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer la configuration
from config import config

def check_database():
    # Utiliser la configuration de développement
    db_uri = config['development'].SQLALCHEMY_DATABASE_URI
    print(f"Connexion à la base de données : {db_uri}")
    
    # Vérifier si c'est SQLite
    if db_uri.startswith('sqlite'):
        db_path = db_uri.replace('sqlite:///', '')
        print(f"Chemin de la base de données SQLite : {db_path}")
        
        # Vérifier si le fichier existe
        if os.path.exists(db_path):
            print(f"Le fichier de base de données existe. Taille : {os.path.getsize(db_path)} octets")
        else:
            print("Le fichier de base de données n'existe pas.")
    
    # Créer un moteur SQLAlchemy
    print("\nCréation du moteur SQLAlchemy...")
    engine = create_engine(db_uri)
    
    # Vérifier la connexion
    try:
        with engine.connect() as conn:
            print("Connexion à la base de données réussie !")
    except Exception as e:
        print(f"ERREUR de connexion à la base de données : {e}")
        return
    
    # Vérifier les tables
    print("\nVérification des tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print("Tables existantes :")
        for table in tables:
            print(f"- {table}")
    else:
        print("Aucune table n'existe dans la base de données.")
    
    # Vérifier si les modèles sont correctement enregistrés
    print("\nVérification des modèles...")
    try:
        from ekay_platform.models import User, Property, PropertyImage
        print("Modèles importés avec succès :")
        print(f"- {User.__tablename__}")
        print(f"- {Property.__tablename__}")
        print(f"- {PropertyImage.__tablename__}")
    except Exception as e:
        print(f"ERREUR lors de l'importation des modèles : {e}")
    
    # Essayer de créer les tables avec un contexte d'application
    print("\nTentative de création des tables...")
    try:
        from app import create_app, db
        
        # Créer une application Flask
        app = create_app()
        
        # Utiliser le contexte d'application
        with app.app_context():
            print("Création des tables dans le contexte d'application...")
            db.create_all()
            print("Création des tables terminée.")
            
            # Vérifier à nouveau les tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if tables:
                print("\nTables après création :")
                for table in tables:
                    print(f"- {table}")
            else:
                print("Aucune table n'a été créée.")
                
    except Exception as e:
        import traceback
        print(f"ERREUR lors de la création des tables : {e}")
        print("\nDétails de l'erreur :")
        traceback.print_exc()

if __name__ == '__main__':
    print("=== Vérification de la configuration de la base de données ===\n")
    check_database()
    print("\n=== Vérification terminée ===")

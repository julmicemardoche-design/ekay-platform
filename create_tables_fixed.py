"""
Script pour forcer la création des tables de la base de données.
"""
import os
import sys
from datetime import datetime, timedelta

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from ekay_platform.models import User, Property, PropertyImage

def create_tables():
    app = create_app()
    
    with app.app_context():
        print("Suppression des tables existantes...")
        db.drop_all()
        
        print("Création des tables...")
        db.create_all()
        
        # Vérifier que les tables ont été créées
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("\nTables créées :")
        for table in tables:
            print(f"- {table}")
            
        if not tables:
            print("Aucune table n'a été créée. Vérifiez les modèles et la configuration de la base de données.")
            return False
            
        return True

if __name__ == '__main__':
    if create_tables():
        print("\nLes tables ont été créées avec succès !")
    else:
        print("\nÉchec de la création des tables.")

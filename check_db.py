"""
Script pour vérifier la configuration de la base de données.
"""
import os
import sys
from sqlalchemy import create_engine, inspect

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

def check_database():
    # Utiliser la configuration de développement
    db_uri = config['development'].SQLALCHEMY_DATABASE_URI
    print(f"Connexion à la base de données : {db_uri}")
    
    # Créer un moteur SQLAlchemy
    engine = create_engine(db_uri)
    
    # Vérifier si le fichier de base de données existe
    if db_uri.startswith('sqlite'):
        db_path = db_uri.replace('sqlite:///', '')
        if os.path.exists(db_path):
            print(f"Le fichier de base de données existe : {db_path}")
            print(f"Taille du fichier : {os.path.getsize(db_path)} octets")
        else:
            print(f"Le fichier de base de données n'existe pas : {db_path}")
    
    # Vérifier les tables existantes
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\nTables dans la base de données :")
    if tables:
        for table in tables:
            print(f"- {table}")
    else:
        print("Aucune table trouvée dans la base de données.")
    
    # Afficher les colonnes de chaque table
    for table in tables:
        print(f"\nStructure de la table '{table}':")
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"- {column['name']} ({column['type']})")

if __name__ == '__main__':
    check_database()

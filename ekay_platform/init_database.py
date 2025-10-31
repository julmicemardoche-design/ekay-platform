"""
Script pour initialiser la base de données.
Exécutez ce script avec la commande : python init_database.py
"""

import os
import sys

# Configuration du chemin Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE_DIR))

# Import de l'application et de la base de données
from ekay_platform import create_app, db
from ekay_platform.models.user import User
from ekay_platform.models.property import Property, PropertyImage

# Création de l'application
app = create_app()

# Création des tables dans le contexte de l'application
with app.app_context():
    print("Création des tables de la base de données...")
    db.create_all()
    db.session.commit()
    print("✅ Base de données initialisée avec succès !")

"""
Script pour initialiser directement la base de données SQLite.
"""
import os
import sqlite3
from datetime import datetime

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ekay_direct.db')

def init_db():
    # Supprimer le fichier de base de données s'il existe
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    # Se connecter à la base de données (créera le fichier s'il n'existe pas)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Créer la table users
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(64) NOT NULL UNIQUE,
        email VARCHAR(120) NOT NULL UNIQUE,
        password_hash VARCHAR(128) NOT NULL,
        phone VARCHAR(20),
        is_landlord BOOLEAN DEFAULT 0,
        is_admin BOOLEAN DEFAULT 0,
        created_at DATETIME NOT NULL,
        last_seen DATETIME NOT NULL
    )
    ''')
    
    # Créer la table properties
    cursor.execute('''
    CREATE TABLE properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        price FLOAT NOT NULL,
        rooms INTEGER NOT NULL,
        address VARCHAR(300) NOT NULL,
        corridor VARCHAR(50),
        color VARCHAR(50),
        is_available BOOLEAN DEFAULT 1,
        available_from DATETIME,
        min_stay INTEGER DEFAULT 12,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Créer la table property_images
    cursor.execute('''
    CREATE TABLE property_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename VARCHAR(255) NOT NULL,
        is_primary BOOLEAN DEFAULT 0,
        created_at DATETIME NOT NULL,
        property_id INTEGER NOT NULL,
        FOREIGN KEY (property_id) REFERENCES properties (id)
    )
    ''')
    
    # Créer la table favorites (many-to-many entre users et properties)
    cursor.execute('''
    CREATE TABLE favorites (
        user_id INTEGER NOT NULL,
        property_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, property_id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (property_id) REFERENCES properties (id)
    )
    ''')
    
    # Ajouter un utilisateur de test
    cursor.execute('''
    INSERT INTO users (username, email, password_hash, is_landlord, created_at, last_seen)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        'testuser',
        'test@example.com',
        'pbkdf2:sha256:260000$GGfESI8gt5cBpqRU$52c4113f81d85526b5dc14950463726483a27b73e0f3f53b1c83753899200118',  # test123
        1,
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    # Ajouter un administrateur
    cursor.execute('''
    INSERT INTO users (username, email, password_hash, is_admin, created_at, last_seen)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        'admin',
        'admin@example.com',
        'pbkdf2:sha256:260000$sHHebSUewPy0bbhm$6e149a28b74ccd014f1f915bf85044ae7813939d11c4fd162b08182b73443944',  # admin123
        1,
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    # Récupérer l'ID de l'utilisateur de test
    user_id = cursor.lastrowid - 1  # Le premier ID est 1, donc l'utilisateur de test a l'ID 1
    
    # Ajouter des propriétés de test
    cursor.execute('''
    INSERT INTO properties (title, description, price, rooms, address, corridor, color, is_available, available_from, min_stay, created_at, updated_at, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Appartement moderne en centre-ville',
        'Bel appartement lumineux avec vue sur la ville',
        750.0,
        3,
        '123 Rue Principale, Ville',
        'A',
        'Bleu',
        1,
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        12,
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        user_id
    ))
    
    cursor.execute('''
    INSERT INTO properties (title, description, price, rooms, address, is_available, available_from, min_stay, created_at, updated_at, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Studio étudiant proche université',
        'Studio meublé idéal pour étudiant',
        450.0,
        1,
        '456 Avenue des Étudiants',
        1,
        (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
        6,
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        user_id
    ))
    
    # Récupérer les IDs des propriétés
    property1_id = cursor.lastrowid - 1
    property2_id = cursor.lastrowid
    
    # Ajouter des images pour les propriétés
    cursor.execute('''
    INSERT INTO property_images (filename, is_primary, created_at, property_id)
    VALUES (?, ?, ?, ?)
    ''', (
        'property1.jpg',
        1,
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        property1_id
    ))
    
    cursor.execute('''
    INSERT INTO property_images (filename, is_primary, created_at, property_id)
    VALUES (?, ?, ?, ?)
    ''', (
        'property2.jpg',
        1,
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        property2_id
    ))
    
    # Valider les changements
    conn.commit()
    
    # Vérifier les tables créées
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("\n=== Base de données initialisée avec succès ! ===")
    print(f"Emplacement : {DB_PATH}")
    print("\nTables créées :")
    for table in tables:
        print(f"- {table[0]}")
    
    print("\nUtilisateurs créés :")
    cursor.execute("SELECT id, username, email, is_admin FROM users")
    for user in cursor.fetchall():
        print(f"- ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Admin: {bool(user[3])}")
    
    print("\nPropriétés créées :")
    cursor.execute("SELECT id, title, price, rooms FROM properties")
    for prop in cursor.fetchall():
        print(f"- ID: {prop[0]}, Titre: {prop[1]}, Prix: {prop[2]}, Pièces: {prop[3]}")
    
    # Fermer la connexion
    conn.close()

if __name__ == '__main__':
    from datetime import timedelta
    print("=== Initialisation de la base de données E-KAY avec SQLite direct ===\n")
    init_db()
    print("\n=== Terminé ===")
    print("\nVous pouvez maintenant démarrer l'application avec 'python app.py'")
    print("Utilisez les identifiants suivants pour vous connecter :")
    print("- Administrateur: admin / admin123")
    print("- Utilisateur test: testuser / test123")

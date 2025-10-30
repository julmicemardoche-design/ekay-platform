"""
Script pour initialiser la base de données directement avec SQLAlchemy.
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from werkzeug.security import generate_password_hash

# Configuration de la base de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'ekay_direct.db')

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URI, echo=True)

# Créer une session
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

# Déclarer la base
Base = declarative_base()

# Définir les modèles
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    phone = Column(String(20))
    is_landlord = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    properties = relationship('Property', back_populates='owner', cascade='all, delete-orphan')
    favorites = relationship('Property', secondary='favorites', back_populates='favorited_by')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Property(Base):
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    rooms = Column(Integer, nullable=False)
    address = Column(String(300), nullable=False)
    corridor = Column(String(50))
    color = Column(String(50))
    is_available = Column(Boolean, default=True)
    available_from = Column(DateTime, default=datetime.utcnow)
    min_stay = Column(Integer, default=12)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relations
    owner = relationship('User', back_populates='properties')
    images = relationship('PropertyImage', back_populates='property', cascade='all, delete-orphan')
    favorited_by = relationship('User', secondary='favorites', back_populates='favorites')
    
    def __repr__(self):
        return f'<Property {self.title}>'

class PropertyImage(Base):
    __tablename__ = 'property_images'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    
    # Relations
    property = relationship('Property', back_populates='images')
    
    def __repr__(self):
        return f'<PropertyImage {self.filename}>'

# Table d'association pour la relation many-to-many entre les utilisateurs et les propriétés favorites
favorites = Table('favorites', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('property_id', Integer, ForeignKey('properties.id'), primary_key=True)
)

def init_db():
    print("Suppression des tables existantes...")
    Base.metadata.drop_all(engine)
    
    print("Création des tables...")
    Base.metadata.create_all(engine)
    
    # Vérifier que les tables ont été créées
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print("\nTables créées avec succès :")
        for table in tables:
            print(f"- {table}")
        
        # Ajouter des données de test
        add_test_data()
    else:
        print("ERREUR : Aucune table n'a été créée.")

def add_test_data():
    print("\nAjout des données de test...")
    
    # Créer un utilisateur de test
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('test123'),
        is_landlord=True
    )
    session.add(user)
    
    # Créer un administrateur
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('admin123'),
        is_admin=True
    )
    session.add(admin)
    
    # Valider les utilisateurs
    session.commit()
    
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
        available_from=datetime.utcnow(),
        min_stay=12,
        user_id=user.id
    )
    session.add(property1)
    
    property2 = Property(
        title='Studio étudiant proche université',
        description='Studio meublé idéal pour étudiant',
        price=450.0,
        rooms=1,
        address='456 Avenue des Étudiants',
        is_available=True,
        available_from=datetime.utcnow(),
        min_stay=6,
        user_id=user.id
    )
    session.add(property2)
    
    # Valider les propriétés
    session.commit()
    
    # Ajouter des images aux propriétés
    image1 = PropertyImage(
        filename='property1.jpg',
        is_primary=True,
        property_id=property1.id
    )
    session.add(image1)
    
    image2 = PropertyImage(
        filename='property2.jpg',
        is_primary=True,
        property_id=property2.id
    )
    session.add(image2)
    
    # Valider les images
    session.commit()
    
    print("\nDonnées de test ajoutées avec succès !")
    print(f"\nUtilisateur de test :")
    print(f"- Nom d'utilisateur: testuser")
    print(f"- Mot de passe: test123")
    print(f"- Email: test@example.com")
    print(f"\nAdministrateur :")
    print(f"- Nom d'utilisateur: admin")
    print(f"- Mot de passe: admin123")
    print(f"- Email: admin@example.com")

if __name__ == '__main__':
    from sqlalchemy import inspect
    
    print("=== Initialisation de la base de données avec SQLAlchemy ===\n")
    init_db()
    
    # Vérifier la base de données
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print("\n=== Base de données initialisée avec succès ! ===")
        print(f"Emplacement : {os.path.abspath('ekay_direct.db')}")
    else:
        print("\n=== Échec de l'initialisation de la base de données ===")

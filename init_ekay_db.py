"""
Script d'initialisation robuste pour la base de donnes E-KAY
"""
import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Ajouter le rpertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer SQLAlchemy directement
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Table, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Configuration de la base de donnes
DATABASE_URI = 'sqlite:///ekay_final.db'
engine = create_engine(DATABASE_URI, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Modles
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
    properties = relationship("Property", back_populates="owner")
    favorites = relationship("Property", secondary="favorites", back_populates="favorited_by")

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
    available_from = Column(DateTime)
    min_stay = Column(Integer, default=12)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relations
    owner = relationship("User", back_populates="properties")
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    favorited_by = relationship("User", secondary="favorites", back_populates="favorites")

class PropertyImage(Base):
    __tablename__ = 'property_images'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    
    # Relations
    property = relationship("Property", back_populates="images")

# Table d'association pour les favoris
favorites = Table('favorites', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('property_id', Integer, ForeignKey('properties.id'), primary_key=True)
)

def init_db():
    # Supprimer toutes les tables existantes
    print("Suppression des tables existantes...")
    Base.metadata.drop_all(engine)
    
    # Crer toutes les tables
    print("Cration des tables...")
    Base.metadata.create_all(engine)
    
    # Vrifier que les tables ontt cres
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("ERREUR : Aucune table n'at cre.")
        return False
        
    print("\nTables cres avec succs :")
    for table in tables:
        print(f"- {table}")
    
    # Ajouter des donnes de test
    add_test_data()
    
    return True

def add_test_data():
    # Ajouter un utilisateur de test
    print("\nAjout d'un utilisateur de test...")
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('test123'),
        is_landlord=True
    )
    session.add(user)
    
    # Ajouter un administrateur
    print("Ajout d'un administrateur...")
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('admin123'),
        is_admin=True
    )
    session.add(admin)
    session.commit()
    
    # Ajouter des proprits de test
    print("\nAjout de proprits de test...")
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
        title='Studiotudiant proche universit',
        description='Studio meubl idal pourtudiant',
        price=450.0,
        rooms=1,
        address='456 Avenue destudiants',
        is_available=True,
        available_from=datetime.utcnow() + timedelta(days=30),
        min_stay=6,
        user_id=user.id
    )
    session.add(property2)
    session.commit()
    
    # Ajouter des images pour les proprits
    print("\nAjout d'images pour les proprits...")
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
    session.commit()
    
    print("\nDonnes de test ajoutes avec succs !")

if __name__ == '__main__':
    print("=== Initialisation de la base de donnes E-KAY ===")
    print("Ce script va :")
    print("1. Supprimer toutes les tables existantes")
    print("2. Crer toutes les tables ncessaires")
    print("3. Ajouter des donnes de test")
    print("4. Configurer l'application pour utiliser la nouvelle base de donnes")
    
    # Initialiser la base de donnes
    if init_db():
        # Mettre jour le fichier .env
        with open('.env', 'w') as f:
            f.write('''FLASK_APP=wsgi.py
FLASK_ENV=development
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire_ici
DATABASE_URL=sqlite:///ekay_final.db
''')
        
        print("\n=== Base de donnes initialise avec succs ! ===")
        print(f"Fichier de base de donnes : {os.path.abspath('ekay_final.db')}")
        print("\nIdentifiants de test :")
        print("- Administrateur : admin / admin123")
        print("- Utilisateur test : testuser / test123")
        print("\nVous pouvez maintenant dmarrer l'application avec :")
        print("  python app.py")
    else:
        print("\n===chec de l'initialisation de la base de donnes ===")

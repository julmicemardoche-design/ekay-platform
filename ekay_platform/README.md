# E-KAY Platform

**Plateforme Collaborative de Location de Logements pour le Village EKAM**

---

## ⚖️ Copyright & License

**© 2025 Walny Mardoché JULMICE - Tous droits réservés / All Rights Reserved**

Ce logiciel et tous ses éléments (code source, design, interface, données, documentation, etc.) sont la propriété exclusive de **Walny Mardoché JULMICE**.

### ⚠️ AVERTISSEMENT LÉGAL

**Toute reproduction, modification, diffusion ou utilisation, partielle ou totale, sans autorisation écrite préalable de l'auteur, est strictement interdite** et constitue une violation du Code de la propriété intellectuelle et des lois internationales sur le droit d'auteur.

L'utilisation de ce logiciel est réservée aux personnes ou entités ayant obtenu une autorisation explicite de l'auteur. Aucune cession ou transfert de droits n'est accordé, sauf stipulation écrite contraire.

**Contact officiel:** julmicemardoche@gmail.com

---

## 📋 Description

E-KAY est une plateforme web moderne de location de logements développée spécifiquement pour le village EKAM. Elle permet aux propriétaires de lister leurs biens immobiliers et aux locataires potentiels de trouver facilement leur logement idéal.

### Fonctionnalités Principales

- 🏠 **Gestion des propriétés** : Ajout, modification et suppression d'annonces
- 👤 **Système d'authentification** : Inscription et connexion sécurisées
- 🔍 **Recherche avancée** : Filtrage par prix, type, nombre de pièces
- 📸 **Galerie d'images** : Upload et affichage de photos de propriétés
- 💬 **Messagerie** : Communication entre propriétaires et locataires
- 📊 **Tableaux de bord** : Interface personnalisée pour landlords et tenants
- 🔔 **Notifications** : Alertes par email
- 📱 **Design responsive** : Compatible mobile, tablette et desktop

---

## 🛠️ Technologies Utilisées

### Backend
- **Python 3.8+**
- **Flask** - Framework web
- **Flask-SQLAlchemy** - ORM pour la base de données
- **Flask-Login** - Gestion de l'authentification
- **Flask-Migrate** - Migrations de base de données
- **Flask-WTF** - Formulaires et validation

### Frontend
- **Bootstrap 5** - Framework CSS responsive
- **Font Awesome** - Icônes
- **JavaScript ES6+** - Interactions dynamiques

### Base de données
- **SQLite** (développement)
- **PostgreSQL** (production)

---

## 📁 Structure du Projet

```
ekay_platform/
│
├── auth/                   # Blueprint d'authentification
│   ├── __init__.py
│   ├── routes.py          # Routes d'authentification
│   └── forms.py           # Formulaires d'authentification
│
├── main/                   # Blueprint principal
│   ├── __init__.py
│   ├── routes.py          # Routes principales
│   ├── forms.py           # Formulaires principaux
│   └── errors.py          # Gestionnaires d'erreurs
│
├── properties/             # Blueprint des propriétés
│   ├── __init__.py
│   ├── routes.py          # Routes des propriétés
│   └── forms.py           # Formulaires des propriétés
│
├── static/                 # Fichiers statiques
│   ├── css/
│   │   └── style.css      # Styles personnalisés
│   ├── js/
│   │   └── main.js        # Scripts JavaScript
│   └── images/            # Images et uploads
│
├── templates/              # Templates HTML
│   ├── base.html          # Template de base
│   ├── auth/              # Templates d'authentification
│   ├── main/              # Templates principales
│   └── properties/        # Templates des propriétés
│
├── __init__.py            # Factory de l'application
├── models.py              # Modèles de base de données
├── config.py              # Configuration
├── LICENSE.txt            # Licence d'utilisation
├── COPYRIGHT              # Notice de copyright
└── README.md              # Ce fichier
```

---

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Virtualenv (recommandé)

### Étapes d'installation

1. **Cloner ou obtenir le projet** (avec autorisation de l'auteur)

2. **Créer un environnement virtuel**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Créer le fichier .env**
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///ekay.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

6. **Initialiser la base de données**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. **Lancer l'application**
```bash
flask run
```

L'application sera accessible à l'adresse: `http://localhost:5000`

---

## 👥 Rôles Utilisateurs

### Locataire (Tenant)
- Rechercher des propriétés
- Voir les détails des annonces
- Contacter les propriétaires
- Gérer ses favoris
- Gérer son profil

### Propriétaire (Landlord)
- Toutes les fonctionnalités du locataire
- Ajouter des propriétés
- Modifier/Supprimer ses propriétés
- Gérer ses annonces
- Recevoir et répondre aux demandes

---

## 🔒 Sécurité

Ce projet implémente plusieurs mesures de sécurité:

- Hachage des mots de passe avec Werkzeug
- Protection CSRF sur tous les formulaires
- Validation des entrées utilisateur
- Sanitisation des données
- Sessions sécurisées
- Protection contre les injections SQL (via SQLAlchemy ORM)

---

## 📧 Contact & Support

**Développeur:** Walny Mardoché JULMICE  
**Email:** julmicemardoche@gmail.com

Pour toute question, demande de fonctionnalité ou rapport de bug, veuillez contacter l'auteur à l'adresse email ci-dessus.

---

## 📜 Mentions Légales

### Propriété Intellectuelle

Ce logiciel est protégé par les lois sur la propriété intellectuelle et le droit d'auteur. Tous les droits, titres et intérêts relatifs à ce logiciel et à sa documentation restent la propriété exclusive de Walny Mardoché JULMICE.

### Utilisation Autorisée

L'utilisation de ce logiciel nécessite une autorisation écrite explicite de l'auteur. Toute utilisation non autorisée peut entraîner des poursuites judiciaires.

### Garanties

CE LOGICIEL EST FOURNI "TEL QUEL", SANS GARANTIE D'AUCUNE SORTE, EXPRESSE OU IMPLICITE. EN AUCUN CAS, L'AUTEUR NE SERA TENU RESPONSABLE DE TOUT DOMMAGE DÉCOULANT DE L'UTILISATION DE CE LOGICIEL.

---

## 🌟 Remerciements

Merci d'utiliser E-KAY Platform. Pour toute demande de licence ou d'utilisation commerciale, veuillez contacter l'auteur.

---

**© 2025 Walny Mardoché JULMICE - Tous droits réservés**

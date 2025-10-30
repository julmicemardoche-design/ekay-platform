# 🏠 E-Kay Platform

[![License](https://img.shields.io/badge/License-Custom-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

> Plateforme de gestion immobilière E-Kay - Solution complète pour la gestion de biens immobiliers

## 🌟 Fonctionnalités

- Gestion des propriétés (ajout, modification, suppression)
- Tableau de bord propriétaire et locataire
- Authentification et gestion des utilisateurs
- Interface utilisateur moderne et réactive
- Gestion des documents et contrats
- Système de messagerie intégré

## 🚀 Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/julmicemardoche-design/ekay-platform.git
   cd ekay-platform
   ```

2. **Créer un environnement virtuel** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : .\venv\Scripts\activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer la base de données** :
   ```bash
   python init_db.py
   ```

5. **Lancer l'application** :
   ```bash
   python run.py
   ```
   L'application sera disponible à l'adresse : http://localhost:5000

## 📁 Structure du projet

```
ekay-platform/
├── ekay_platform/          # Code source principal
│   ├── static/             # Fichiers statiques (CSS, JS, images)
│   ├── templates/          # Templates HTML
│   ├── auth/               # Authentification
│   ├── main/               # Module principal
│   ├── properties/         # Gestion des propriétés
│   ├── __init__.py
│   ├── config.py
│   └── models.py
├── tests/                  # Tests unitaires
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── run.py
```

## 🔧 Configuration

Copiez le fichier `.env.example` vers `.env` et modifiez les paramètres selon votre configuration :

```bash
cp .env.example .env
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment procéder :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence personnalisée. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📧 Contact

Julmice Mardoché - [julmicemardoche@gmail.com](mailto:julmicemardoche@gmail.com)

Lien du projet : [https://github.com/julmicemardoche-design/ekay-platform](https://github.com/julmicemardoche-design/ekay-platform)
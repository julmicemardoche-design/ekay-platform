import os
import tempfile
import pytest
from flask import template_rendered
from ekay_platform import create_app, db
from ekay_platform.models import User, Property

# Configuration de l'application pour les tests
class TestConfig:
    """Configuration pour les tests."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    PROPERTIES_PER_PAGE = 10
    
    @staticmethod
    def init_app(app):
        """Initialisation de l'application pour les tests."""
        pass

# S'assurer que la configuration de test est disponible dans config
from config import config as app_config
app_config['testing'] = TestConfig

@pytest.fixture
def app():
    """Création et configuration d'une nouvelle application pour chaque test."""
    # Créer un fichier temporaire pour la base de données
    db_fd, db_path = tempfile.mkstemp()
    
    # Utiliser la configuration de test
    app = create_app('testing')
    
    # Mettre à jour l'URI de la base de données avec le fichier temporaire
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Créer la base de données et charger les données de test
    with app.app_context():
        db.create_all()
        # Créer un utilisateur de test
        user = User(
            username='testuser',
            email='test@example.com',
            password='password'
        )
        db.session.add(user)
        db.session.commit()

    yield app

    # Nettoyer après le test
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Un client de test pour l'application."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Un test runner pour les commandes CLI."""
    return app.test_cli_runner()

class AuthActions:
    """Classe utilitaire pour les tests d'authentification."""
    def __init__(self, client):
        self._client = client
    
    def login(self, username='testuser', password='password'):
        # D'abord, récupérer la page de connexion pour obtenir le jeton CSRF
        login_page = self._client.get('/auth/login')
        assert login_page.status_code == 200
        
        # Extraire le jeton CSRF du formulaire
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(login_page.data, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_input:
            # Si le jeton CSRF n'est pas trouvé, essayer de l'extraire directement du HTML
            csrf_token_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.data.decode('utf-8'))
            if csrf_token_match:
                csrf_token = csrf_token_match.group(1)
            else:
                # Si le jeton CSRF n'est toujours pas trouvé, essayer de se connecter sans
                return self._client.post(
                    '/auth/login',
                    data={'username': username, 'password': password},
                    follow_redirects=True
                )
        else:
            csrf_token = csrf_input['value']
        
        # Envoyer la requête de connexion avec le jeton CSRF
        return self._client.post(
            '/auth/login',
            data={
                'username': username,
                'password': password,
                'csrf_token': csrf_token
            },
            follow_redirects=True
        )
    
    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True)

@pytest.fixture
def auth(client):
    return AuthActions(client)

@pytest.fixture
def captured_templates(app):
    """Capture les templates rendus pendant le test."""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

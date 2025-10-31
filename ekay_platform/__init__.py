"""
E-KAY Platform - Collaborative Housing Rental Platform
"""

import os
import sys
from flask import Flask
from datetime import datetime

# Configuration du chemin Python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Import des extensions
from .extensions import db, login_manager, migrate, mail, babel

# Import de la configuration
from config import config

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    babel.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .properties import properties as properties_blueprint
    app.register_blueprint(properties_blueprint, url_prefix='/properties')
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .user.routes import bp as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')
    
    # Ajouter la variable 'now' au contexte de Jinja2
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}
    
    from .admin import admin_bp as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    # Error handlers
    from .errors import page_not_found, internal_server_error, forbidden
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(403, forbidden)
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from .models import User, Property, PropertyImage
        return {
            'db': db,
            'User': User,
            'Property': Property,
            'PropertyImage': PropertyImage
        }
    
    return app


# Import des modèles pour s'assurer qu'ils sont enregistrés avec SQLAlchemy
# Cette importation est nécessaire pour que SQLAlchemy connaisse tous les modèles
# avant de créer les tables de la base de données
from .models import User, Property, PropertyImage, Token  # noqa: F401

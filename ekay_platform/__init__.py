"""
E-KAY Platform - Collaborative Housing Rental Platform
Copyright (c) 2025 Walny Mardoché JULMICE. All Rights Reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.
Contact: julmicemardoche@gmail.com
"""

import os
import sys
from flask import Flask

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Maintenant, nous pouvons importer config
from config import config

from .extensions import db, login_manager, migrate, mail

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


# Import models to ensure they are registered with SQLAlchemy
from .models import User, Property, PropertyImage

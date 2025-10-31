from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Import des extensions et modèles
from ..extensions import db
from ..models.user import User

# Import des formulaires et utilitaires
from .forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from ..email_utils import send_password_reset_email

# Create a Blueprint for authentication routes
auth = Blueprint('auth', __name__)

# Import routes at the bottom to avoid circular imports
from . import routes

# This file serves as the entry point for the auth blueprint
# All route handlers are defined in routes.py to keep the code organized

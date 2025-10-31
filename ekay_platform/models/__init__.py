"""
E-KAY Platform - Models Package
"""

# Import des modèles pour les rendre disponibles au niveau du package
from .user import User
from .property import Property, PropertyImage
from .tokens import Token
from .associations import favorites

# Initialisation des relations circulaires après l'import de tous les modèles
from . import user as _  # noqa: F401

__all__ = ['User', 'Property', 'PropertyImage', 'Token', 'favorites']

"""
E-KAY Platform - User Routes
Copyright (c) 2025 Walny Mardoché JULMICE. All Rights Reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.
Contact: julmicemardoche@gmail.com
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp

@bp.route('/profile')
@login_required
def profile():
    """Afficher le profil de l'utilisateur"""
    return render_template('user/profile.html', title='Mon Profil')

@bp.route('/properties')
@login_required
def properties():
    """Afficher les propriétés de l'utilisateur"""
    return render_template('user/properties.html', title='Mes Annonces')

@bp.route('/favorites')
@login_required
def favorites():
    """Afficher les favoris de l'utilisateur"""
    return render_template('user/favorites.html', title='Mes Favoris')

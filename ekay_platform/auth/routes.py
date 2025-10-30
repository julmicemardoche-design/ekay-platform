"""
E-KAY Platform - Authentication Routes
Copyright (c) 2025 Walny Mardoché JULMICE. All Rights Reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.
Contact: julmicemardoche@gmail.com
"""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from . import auth
from .. import db
from ..models import User
from .forms import (LoginForm, RegistrationForm, EditProfileForm,
                   ResetPasswordRequestForm, ResetPasswordForm)
from ..email import send_password_reset_email

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        
        flash('Vérifiez votre email pour les instructions de réinitialisation du mot de passe', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html',
                         title='Réinitialiser le mot de passe', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Lien de réinitialisation invalide ou expiré', 'warning')
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        
        flash('Votre mot de passe a été réinitialisé avec succès.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.commit()
            flash('Votre mot de passe a été mis à jour.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Mot de passe actuel incorrect.', 'danger')
    
    return render_template('auth/change_password.html', title='Changer de mot de passe', form=form)

@auth.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    # In a real app, you might want to anonymize data instead of deleting it
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    flash('Votre compte a été supprimé avec succès.', 'info')
    return redirect(url_for('main.index'))

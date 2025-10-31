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
                   ResetPasswordRequestForm, ResetPasswordForm, ResendVerificationForm, ChangePasswordForm)
from ..email_utils import send_password_reset_email, send_verification_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Gère la connexion des utilisateurs"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Recherche par nom d'utilisateur ou email
        user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.username.data)
        ).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Nom d\'utilisateur/email ou mot de passe invalide', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
            
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Connexion', form=form)


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

@auth.route('/verify-email/<token>')
def verify_email(token):
    if current_user.is_authenticated and current_user.email_verified:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(id=current_user.get_id()).first()
    if not user:
        flash('Utilisateur non trouvé. Veuillez vous connecter.', 'warning')
        return redirect(url_for('auth.login'))
    
    if user.verify_token(token, 'email_verification'):
        user.verify_email()
        flash('Votre adresse email a été vérifiée avec succès !', 'success')
        return redirect(url_for('main.dashboard'))
    
    flash('Le lien de vérification est invalide ou a expiré.', 'danger')
    return redirect(url_for('auth.resend_verification'))

@auth.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if current_user.is_authenticated and current_user.email_verified:
        return redirect(url_for('main.index'))
    
    form = ResendVerificationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and not user.email_verified:
            send_verification_email(user)
            flash('Un nouvel email de vérification a été envoyé à votre adresse.', 'info')
            return redirect(url_for('auth.login'))
        flash('Cette adresse email est déjà vérifiée ou n\'existe pas.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/resend_verification.html', form=form)

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

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            is_landlord=form.is_landlord.data,
            email_verified=False
        )
        user.password = form.password.data
        
        db.session.add(user)
        db.session.commit()
        
        # Envoyer l'email de vérification
        send_verification_email(user)
        
        flash('Inscription réussie ! Un email de vérification a été envoyé à votre adresse email.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Inscription', form=form)

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


@auth.route('/logout')
@login_required
def logout():
    """Déconnexion de l'utilisateur"""
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('main.index'))

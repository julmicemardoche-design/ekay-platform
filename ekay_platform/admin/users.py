"""
E-KAY Platform - Admin Users Management
"""
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .. import db
from ..models import User
from . import admin_bp
from .forms import UserForm, UserEditForm

@admin_bp.route('/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    
    return render_template('admin/users.html', 
                         title='Gestion des utilisateurs',
                         users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    if not current_user.is_admin:
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            is_admin=form.is_admin.data,
            is_landlord=form.is_landlord.data,
            email_verified=form.email_verified.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Utilisateur créé avec succès!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/user_form.html', 
                         title='Nouvel utilisateur',
                         form=form)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        user.is_landlord = form.is_landlord.data
        user.email_verified = form.email_verified.data
        
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('Utilisateur mis à jour avec succès!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/user_form.html', 
                         title='Modifier utilisateur',
                         form=form, 
                         user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    if current_user.id == user_id:
        flash('Vous ne pouvez pas supprimer votre propre compte!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash('Utilisateur supprimé avec succès!', 'success')
    return redirect(url_for('admin.manage_users'))

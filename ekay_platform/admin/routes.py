from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .. import db
from ..models import Property, User
from ..properties.forms import PropertyForm
from . import admin_bp

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    properties = Property.query.all()
    return render_template('admin/dashboard.html', title='Tableau de bord', properties=properties)

@admin_bp.route('/admin/property/new', methods=['GET', 'POST'])
@login_required
def new_property():
    if not current_user.is_admin:
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(
            title=form.title.data,
            description=form.description.data,
            price=form.price_info.price.data,
            price_type=form.price_info.price_type.data,
            property_type=form.details.property_type.data,
            rooms=form.details.rooms.data,
            bedrooms=form.details.bedrooms.data,
            bathrooms=form.details.bathrooms.data,
            surface=form.details.surface.data,
            address=form.location.address.data,
            city=form.location.city.data,
            postal_code=form.location.postal_code.data,
            country=form.location.country.data,
            is_available=form.availability.is_available.data,
            available_from=form.availability.available_from.data,
            owner_id=current_user.id
        )
        
        # Gestion de l'image principale
        if form.main_image.data:
            image = form.main_image.data
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'properties', filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
            property.main_image = f'properties/{filename}'
        
        db.session.add(property)
        db.session.commit()
        flash('Le bien a été ajouté avec succès!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/property_form.html', title='Ajouter un bien', form=form)

@admin_bp.route('/admin/property/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(id):
    if not current_user.is_admin:
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    property = Property.query.get_or_404(id)
    form = PropertyForm(obj=property)
    
    if form.validate_on_submit():
        property.title = form.title.data
        property.description = form.description.data
        property.price = form.price_info.price.data
        property.price_type = form.price_info.price_type.data
        property.property_type = form.details.property_type.data
        property.rooms = form.details.rooms.data
        property.bedrooms = form.details.bedrooms.data
        property.bathrooms = form.details.bathrooms.data
        property.surface = form.details.surface.data
        property.address = form.location.address.data
        property.city = form.location.city.data
        property.postal_code = form.location.postal_code.data
        property.country = form.location.country.data
        property.is_available = form.availability.is_available.data
        property.available_from = form.availability.available_from.data
        
        # Gestion de l'image principale
        if form.main_image.data:
            # Supprimer l'ancienne image si elle existe
            if property.main_image:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], property.main_image))
                except:
                    pass
            
            image = form.main_image.data
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'properties', filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
            property.main_image = f'properties/{filename}'
        
        db.session.commit()
        flash('Le bien a été mis à jour avec succès!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/property_form.html', title='Modifier le bien', form=form, property=property)

@admin_bp.route('/admin/property/<int:id>/delete', methods=['POST'])
@login_required
def delete_property(id):
    if not current_user.is_admin:
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect(url_for('main.index'))
    
    property = Property.query.get_or_404(id)
    
    # Supprimer l'image associée si elle existe
    if property.main_image:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], property.main_image))
        except:
            pass
    
    db.session.delete(property)
    db.session.commit()
    flash('Le bien a été supprimé avec succès!', 'success')
    return redirect(url_for('admin.admin_dashboard'))

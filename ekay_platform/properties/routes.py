from flask import (
    render_template, redirect, url_for, flash, 
    request, current_app, abort, jsonify, send_from_directory
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
import os
import uuid

from . import properties
from ..extensions import db
from ..models import Property, PropertyImage, User
from .forms import PropertyForm, PropertyImageForm, PropertySearchForm
from .booking_forms import BookingForm
from ..email_utils import send_property_approved_email, send_booking_confirmation, send_booking_notification
from ..utils import save_property_image, delete_property_images, allowed_file

# Nombre de propriétés par page pour la pagination
PROPERTIES_PER_PAGE = 12

@properties.route('/')
@properties.route('/search')
def list_properties():
    """Affiche la liste des propriétés avec filtres de recherche"""
    # Initialiser le formulaire de recherche avec les paramètres de l'URL
    search_form = PropertySearchForm()
    
    # Construire la requête de base
    query = Property.query.filter_by(is_available=True)
    
    # Appliquer les filtres
    if search_form.validate():
        # Filtre par type de bien
        if search_form.property_type.data:
            query = query.filter(Property.property_type == search_form.property_type.data)
        
        # Filtre par prix
        if search_form.min_price.data:
            query = query.filter(Property.price >= search_form.min_price.data)
        if search_form.max_price.data:
            query = query.filter(Property.price <= search_form.max_price.data)
        
        # Filtre par nombre de pièces
        if search_form.min_rooms.data > 0:
            query = query.filter(Property.rooms >= search_form.min_rooms.data)
        
        # Filtre par caractéristiques
        if search_form.has_kitchen.data:
            query = query.filter_by(has_kitchen=True)
        if search_form.has_parking.data:
            query = query.filter_by(has_parking=True)
        if search_form.has_garden.data:
            query = query.filter_by(has_garden=True)
        if search_form.has_balcony.data:
            query = query.filter_by(has_balcony=True)
        if search_form.has_pool.data:
            query = query.filter_by(has_pool=True)
        if search_form.is_furnished.data:
            query = query.filter_by(is_furnished=True)
        
        # Filtre par disponibilité
        if search_form.available_soon.data:
            query = query.filter(Property.available_from <= datetime.utcnow())
    
    # Trier les résultats
    sort_by = request.args.get('sort_by', 'newest')
    if sort_by == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Property.price.desc())
    elif sort_by == 'area_desc':
        query = query.order_by(Property.area.desc())
    else:  # Par défaut, trier par date de création décroissante
        query = query.order_by(Property.created_at.desc())
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    properties_pagination = query.paginate(
        page=page, 
        per_page=PROPERTIES_PER_PAGE,
        error_out=False
    )
    
    # Pour le formulaire de recherche, conserver les valeurs sélectionnées
    if request.method == 'GET':
        for field in search_form:
            if field.name in request.args:
                field.data = request.args.get(field.name)
    
    return render_template(
        'properties/list.html',
        properties=properties_pagination,
        search_form=search_form,
        sort_by=sort_by
    )

@properties.route('/<int:id>')
def view_property(id):
    """Affiche les détails d'une propriété"""
    property = Property.query.get_or_404(id)
    
    # Vérifier si l'utilisateur est le propriétaire
    is_owner = current_user.is_authenticated and property.user_id == current_user.id
    
    # Incrémenter le compteur de vues si l'utilisateur n'est pas le propriétaire
    if not is_owner:
        property.increment_views()
    
    # Récupérer les propriétés similaires (même type, même ville)
    similar_properties = Property.query.filter(
        Property.id != property.id,
        Property.property_type == property.property_type,
        Property.city == property.city,
        Property.is_available == True
    ).order_by(db.func.random()).limit(4).all()
    
    return render_template(
        'properties/detail.html',
        property=property,
        is_owner=is_owner,
        similar_properties=similar_properties
    )

@properties.route('/new', methods=['GET', 'POST'])
@login_required
def new_property():
    """Crée une nouvelle annonce de propriété avec le formulaire amélioré"""
    form = PropertyForm()
    
    # Pré-remplir les champs de contact avec les informations de l'utilisateur
    if not form.contact_name.data and current_user.is_authenticated:
        form.contact_name.data = current_user.full_name
        form.contact_phone.data = current_user.phone
        form.contact_email.data = current_user.email
    
    if form.validate_on_submit():
        action = request.form.get('action', 'save_draft')
        status = 'draft' if action == 'save_draft' else 'pending'
        
        try:
            # Déterminer le prix mensuel et annuel en fonction du type de prix sélectionné
            if form.price_info.price_type.data == 'monthly':
                price = float(form.price_info.price.data) if form.price_info.price.data else 0
                annual_price = price * 12 if price > 0 else None
            else:
                annual_price = float(form.price_info.price.data) if form.price_info.price.data else 0
                price = annual_price / 12 if annual_price > 0 else 0
                
            # Créer une nouvelle propriété avec les données du formulaire
            property_data = {
                'title': form.title.data,
                'description': form.description.data,
                'property_type': form.property_type.data,
                'transaction_type': form.transaction_type.data,
                'price': price,
                'annual_price': annual_price,
                'price_type': form.price_info.price_type.data,
                'currency': form.price_info.currency.data,
                'area': form.area.data,
                'rooms': form.rooms.data,
                'bedrooms': form.bedrooms.data or 0,
                'bathrooms': form.bathrooms.data or 0,
                'year_built': form.year_built.data,
                'floor': form.floor.data,
                'total_floors': form.total_floors.data,
                'address': form.address.data,
                'city': form.city.data,
                'state': form.state.data,
                'postal_code': form.postal_code.data,
                'country': form.country.data,
                'latitude': form.latitude.data or None,
                'longitude': form.longitude.data or None,
                'has_kitchen': form.has_kitchen.data or False,
                'has_parking': form.has_parking.data or False,
                'has_garden': form.has_garden.data or False,
                'has_balcony': form.has_balcony.data or False,
                'has_pool': form.has_pool.data or False,
                'has_elevator': form.has_elevator.data or False,
                'has_air_conditioning': form.has_air_conditioning.data or False,
                'has_heating': form.has_heating.data or False,
                'is_furnished': form.is_furnished.data or False,
                'is_new_construction': form.is_new_construction.data or False,
                'security_deposit': form.price_info.security_deposit.data or 0,
                'available_from': form.available_from.data,
                'minimum_rent_days': form.minimum_rent_days.data or 1,
                'allows_pets': form.allows_pets.data or False,
                'allows_smoking': form.allows_smoking.data or False,
                'allows_events': form.allows_events.data or False,
                'contact_name': form.contact_name.data or current_user.full_name,
                'contact_phone': form.contact_phone.data or current_user.phone,
                'contact_email': form.contact_email.data or current_user.email,
                'status': status,
                'user_id': current_user.id,
                'is_featured': form.is_featured.data and current_user.is_admin,
                'is_premium': form.is_premium.data and current_user.is_premium,
                'construction_year': form.construction_year.data,
                'land_area': form.land_area.data,
                'furnishing_type': form.furnishing_type.data,
                'condition': form.condition.data,
                'orientation': form.orientation.data,
                'view': form.view.data,
                'heating_type': form.heating_type.data,
                'energy_efficiency_rating': form.energy_efficiency_rating.data,
                'has_wardrobes': form.has_wardrobes.data or False,
                'has_dishwasher': form.has_dishwasher.data or False,
                'has_washing_machine': form.has_washing_machine.data or False,
                'has_dryer': form.has_dryer.data or False,
                'has_tv': form.has_tv.data or False,
                'has_internet': form.has_internet.data or False,
                'has_terrace': form.has_terrace.data or False,
                'has_security': form.has_security.data or False,
                'has_intercom': form.has_intercom.data or False,
                'has_caretaker': form.has_caretaker.data or False,
                'has_gym': form.has_gym.data or False,
                'has_doorman': form.has_doorman.data or False,
                'has_pet_friendly': form.has_pet_friendly.data or False,
                'has_wheelchair_access': form.has_wheelchair_access.data or False,
                'has_concierge': form.has_concierge.data or False,
                'has_laundry': form.has_laundry.data or False,
                'has_storage': form.has_storage.data or False,
                'has_covered_parking': form.has_covered_parking.data or False,
                'has_garage': form.has_garage.data or False,
                'has_private_garden': form.has_private_garden.data or False,
                'has_shared_garden': form.has_shared_garden.data or False,
                'has_roof_terrace': form.has_roof_terrace.data or False,
                'has_balcony_terrace': form.has_balcony_terrace.data or False,
                'has_sea_view': form.has_sea_view.data or False,
                'has_mountain_view': form.has_mountain_view.data or False,
                'has_city_view': form.has_city_view.data or False,
                'has_pool_view': form.has_pool_view.data or False
            }
            
            # Créer l'objet Property
            property = Property(**{k: v for k, v in property_data.items() if v is not None})
            
            db.session.add(property)
            db.session.flush()  # Pour obtenir l'ID avant le commit
            
            # Gérer le téléchargement des images
            if 'images' in request.files:
                for file in request.files.getlist('images'):
                    if file and allowed_file(file.filename):
                        # Sauvegarder l'image et créer les miniatures
                        image_data = save_property_image(file, property.id)
                        if image_data:
                            image = PropertyImage(
                                filename=image_data['filename'],
                                original_filename=secure_filename(file.filename),
                                file_size=image_data['file_size'],
                                content_type=file.content_type,
                                width=image_data['width'],
                                height=image_data['height'],
                                property_id=property.id,
                                is_primary=len(property.images.all()) == 0  # Première image = image principale
                            )
                            db.session.add(image)
            
            db.session.commit()
            
            # Message de confirmation approprié
            if status == 'draft':
                flash('Votre brouillon a été enregistré avec succès.', 'success')
            elif current_user.is_admin:
                flash('Votre annonce a été publiée avec succès!', 'success')
            else:
                flash('Votre annonce a été soumise avec succès et est en attente de validation par un administrateur.', 'info')
            
            return redirect(url_for('properties.view_property', id=property.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la création de l'annonce: {e}", exc_info=True)
            flash('Une erreur est survenue lors de la création de l\'annonce. Veuillez vérifier les informations et réessayer.', 'danger')
    
    # Valeurs par défaut pour le formulaire
    if not form.is_submitted():
        # Pré-remplir avec les informations de l'utilisateur si disponibles
        form.contact_name.data = current_user.full_name
        form.contact_phone.data = current_user.phone
        form.contact_email.data = current_user.email
        form.country.data = 'Haïti'
        form.price_info.currency.data = 'USD'  # Devise par défaut
        form.minimum_rent_days.data = 1
    
    # Rendre le template avec le formulaire
    return render_template('properties/property_form.html', 
                         form=form, 
                         title='Publier une nouvelle annonce',
                         action=url_for('properties.new_property'))
        

@properties.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(id):
    """Modifie une annonce existante"""
    property = Property.query.get_or_404(id)
    
    # Vérifier que l'utilisateur est le propriétaire ou un administrateur
    if property.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = PropertyForm(obj=property)
    
    # Initialiser les champs de prix en fonction des données existantes
    if property.annual_price and property.annual_price > 0 and property.annual_price != property.price * 12:
        # Si un prix annuel personnalisé est défini, afficher le prix annuel
        form.price_info.price_type.data = 'annual'
        form.price_info.price.data = property.annual_price
        form.price_info.alternate_price.data = property.price
    else:
        # Sinon, afficher le prix mensuel par défaut
        form.price_info.price_type.data = 'monthly'
        form.price_info.price.data = property.price
        form.price_info.alternate_price.data = property.price * 12 if property.price else ''
    
    if form.validate_on_submit():
        try:
            # Mettre à jour les champs de la propriété
            property.title = form.title.data
            property.description = form.description.data
            # Déterminer le prix mensuel et annuel en fonction du type de prix sélectionné
            if form.price_info.price_type.data == 'monthly':
                price = float(form.price_info.price.data) if form.price_info.price.data else 0
                annual_price = price * 12 if price > 0 else None
            else:
                annual_price = float(form.price_info.price.data) if form.price_info.price.data else 0
                price = annual_price / 12 if annual_price > 0 else 0
            property.price = price
            property.annual_price = annual_price
            property.price_type = form.price_info.price_type.data
            property.rooms = form.rooms.data
            property.bedrooms = form.bedrooms.data or None
            property.bathrooms = form.bathrooms.data or 1
            property.area = form.area.data
            property.address = form.address.data
            property.city = form.city.data
            property.state = form.state.data or None
            property.country = form.country.data
            property.has_kitchen = form.has_kitchen.data
            property.has_parking = form.has_parking.data
            property.has_garden = form.has_garden.data
            property.has_balcony = form.has_balcony.data
            property.has_pool = form.has_pool.data
            property.is_furnished = form.is_furnished.data
            property.available_from = form.available_from.data
            property.min_stay = form.min_stay.data
            
            # Seul un administrateur peut mettre en avant une annonce
            if current_user.is_admin:
                property.is_featured = form.is_featured.data
            
            # Mettre à jour les images si de nouvelles sont téléchargées
            if 'images' in request.files:
                for file in request.files.getlist('images'):
                    if file and allowed_file(file.filename):
                        image_data = save_property_image(file, property.id)
                        if image_data:
                            image = PropertyImage(
                                filename=image_data['filename'],
                                original_filename=secure_filename(file.filename),
                                file_size=image_data['file_size'],
                                content_type=file.content_type,
                                width=image_data['width'],
                                height=image_data['height'],
                                property_id=property.id
                            )
                            db.session.add(image)
            
            db.session.commit()
            flash('Votre annonce a été mise à jour avec succès!', 'success')
            return redirect(url_for('properties.view_property', id=property.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la mise à jour de l'annonce: {e}")
            flash('Une erreur est survenue lors de la mise à jour de l\'annonce. Veuillez réessayer.', 'danger')
    
    # Pré-remplir le formulaire avec les données existantes
    if not form.is_submitted():
        form.populate_obj(property)
    
    return render_template('properties/form.html',
                         form=form,
                         property=property,
                         title='Modifier l\'annonce',
                         action=url_for('properties.edit_property', id=id))

@properties.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_property(id):
    """Supprime une annonce"""
    property = Property.query.get_or_404(id)
    
    # Vérifier que l'utilisateur est le propriétaire ou un administrateur
    if property.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    try:
        # Supprimer les images associées
        for image in property.images.all():
            delete_property_images(image)
        
        # Supprimer la propriété
        db.session.delete(property)
        db.session.commit()
        
        flash('L\'annonce a été supprimée avec succès.', 'success')
        return redirect(url_for('properties.list_properties'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la suppression de l'annonce: {e}")
        flash('Une erreur est survenue lors de la suppression de l\'annonce. Veuillez réessayer.', 'danger')
        return redirect(url_for('properties.view_property', id=id))

@properties.route('/<int:property_id>/images/<int:image_id>/set-primary', methods=['POST'])
@login_required
def set_primary_image(property_id, image_id):
    """Définit une image comme image principale"""
    property = Property.query.get_or_404(property_id)
    
    # Vérifier que l'utilisateur est le propriétaire ou un administrateur
    if property.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Réinitialiser toutes les images principales
    PropertyImage.query.filter_by(property_id=property_id).update({'is_primary': False})
    
    # Définir la nouvelle image principale
    image = PropertyImage.query.filter_by(id=image_id, property_id=property_id).first_or_404()
    image.is_primary = True
    
    db.session.commit()
    
    return jsonify({'success': True})

@properties.route('/<int:property_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_image(property_id, image_id):
    """Supprime une image d'une annonce"""
    property = Property.query.get_or_404(property_id)
    
    # Vérifier que l'utilisateur est le propriétaire ou un administrateur
    if property.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    image = PropertyImage.query.filter_by(id=image_id, property_id=property_id).first_or_404()
    
    try:
        # Supprimer les fichiers d'image
        delete_property_images(image)
        
        # Supprimer l'entrée de la base de données
        db.session.delete(image)
        db.session.commit()
        
        # Si c'était l'image principale, définir une nouvelle image principale
        if image.is_primary:
            first_image = PropertyImage.query.filter_by(property_id=property_id).first()
            if first_image:
                first_image.is_primary = True
                db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la suppression de l'image: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@properties.route('/<int:property_id>/toggle-availability', methods=['POST'])
@login_required
def toggle_availability(property_id):
    """Bascule la disponibilité d'une propriété"""
    property = Property.query.get_or_404(property_id)
    
    # Vérifier que l'utilisateur est le propriétaire ou un administrateur
    if property.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    property.is_available = not property.is_available
    db.session.commit()
    
    status = 'disponible' if property.is_available else 'indisponible'
    flash(f'Votre annonce est maintenant marquée comme {status}.', 'success')
    
    return redirect(url_for('properties.view_property', id=property_id))

@properties.route('/<int:property_id>/contact', methods=['GET', 'POST'])
@login_required
def contact_owner(property_id):
    """Affiche le formulaire de contact pour une propriété"""
    property = Property.query.get_or_404(property_id)
    owner = User.query.get_or_404(property.user_id)
    
    # Empêcher les utilisateurs de se contacter eux-mêmes
    if current_user.id == owner.id:
        return redirect(url_for('properties.view_property', id=property_id))
    
    form = ContactForm()
    
    if form.validate_on_submit():
        try:
            # Envoyer l'email au propriétaire
            send_contact_email(
                to=owner.email,
                sender=current_user.email,
                property=property,
                message=form.message.data,
                name=current_user.username
            )
            
            flash('Votre message a été envoyé au propriétaire avec succès!', 'success')
            return redirect(url_for('properties.view_property', id=property_id))
            
        except Exception as e:
            current_app.logger.error(f"Erreur lors de l'envoi du message: {e}")
            flash('Une erreur est survenue lors de l\'envoi du message. Veuillez réessayer.', 'danger')
    
    return render_template('properties/contact.html',
                         property=property,
                         owner=owner,
                         form=form)

@properties.route('/<int:property_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(property_id):
    """Ajoute ou supprime une propriété des favoris"""
    property = Property.query.get_or_404(property_id)
    
    if property in current_user.favorites:
        current_user.favorites.remove(property)
        action = 'removed'
    else:
        current_user.favorites.append(property)
        action = 'added'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'action': action,
        'favorites_count': len(current_user.favorites)
    })

@properties.route('/favorites')
@login_required
def favorites():
    """Affiche la liste des propriétés favorites de l'utilisateur"""
    page = request.args.get('page', 1, type=int)
    favorites_pagination = current_user.favorites.paginate(
        page=page,
        per_page=PROPERTIES_PER_PAGE,
        error_out=False
    )
    
    return render_template('properties/favorites.html',
                         favorites=favorites_pagination)

@properties.route('/<int:property_id>/report', methods=['POST'])
@login_required
def report_property(property_id):
    """Signale une annonce inappropriée"""
    property = Property.query.get_or_404(property_id)
    
    # Vérifier que l'utilisateur n'est pas le propriétaire
    if property.user_id == current_user.id:
        abort(400, 'Vous ne pouvez pas signaler votre propre annonce.')
    
    # Envoyer une notification à l'administrateur
    try:
        send_property_report_email(property, current_user)
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"Erreur lors du signalement de l'annonce: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Routes API pour l'autocomplétion
@properties.route('/api/cities')
def api_cities():
    """API pour l'autocomplétion des villes"""
    query = request.args.get('q', '').lower()
    
    # Récupérer les villes correspondant à la requête
    cities = db.session.query(
        Property.city.distinct().label('city')
    ).filter(
        Property.city.ilike(f'%{query}%')
    ).order_by(
        Property.city
    ).limit(10).all()
    
    return jsonify([city.city for city in cities])

@properties.route('/api/neighborhoods')
def api_neighborhoods():
    """API pour l'autocomplétion des quartiers"""
    query = request.args.get('q', '').lower()
    city = request.args.get('city', '')
    
    # Construire la requête
    q = db.session.query(
        Property.address.distinct().label('address')
    ).filter(
        Property.address.ilike(f'%{query}%')
    )
    
    if city:
        q = q.filter(Property.city == city)
    
    # Exécuter la requête
    addresses = q.order_by(
        Property.address
    ).limit(10).all()
    
    # Extraire les noms de quartiers (simplifié)
    neighborhoods = set()
    for addr in addresses:
        # Essayons d'extraire le nom du quartier (c'est une approximation)
        parts = [p.strip() for p in addr.address.split(',') if p.strip()]
        if len(parts) > 1:
            neighborhoods.add(parts[0])  # Le premier élément est souvent le quartier
    
    return jsonify(sorted(list(neighborhoods)))

# Gestion des erreurs
@properties.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@properties.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@properties.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Routes pour la réservation
@properties.route('/property/<int:property_id>/book', methods=['GET', 'POST'])
@login_required
def book_property(property_id):
    """Affiche le formulaire de réservation et traite la soumission"""
    property = Property.query.get_or_404(property_id)
    
    # Vérifier si la propriété est disponible à la location
    if not property.is_available:
        flash('Cette propriété n\'est plus disponible à la location.', 'danger')
        return redirect(url_for('properties.view_property', id=property_id))
    
    form = BookingForm()
    
    if form.validate_on_submit():
        # Vérifier la disponibilité pour les dates sélectionnées
        if not is_property_available(property_id, form.start_date.data, form.end_date.data):
            flash('Désolé, la propriété n\'est plus disponible pour les dates sélectionnées.', 'danger')
            return render_template('properties/booking.html', property=property, form=form)
        
        # Créer la réservation
        booking = Booking(
            property_id=property_id,
            user_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            guests=form.guests.data,
            notes=form.notes.data,
            status='pending'  # En attente de confirmation
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Envoyer les emails de confirmation
        send_booking_confirmation(booking)
        send_booking_notification(booking, property.user)
        
        flash('Votre demande de réservation a été envoyée avec succès ! Le propriétaire vous contactera bientôt.', 'success')
        return redirect(url_for('properties.booking_details', booking_id=booking.id))
    
    return render_template('properties/booking.html', property=property, form=form)

def is_property_available(property_id, start_date, end_date):
    """Vérifie si une propriété est disponible pour les dates données"""
    # Vérifier s'il y a des réservations qui se chevauchent
    overlapping_bookings = Booking.query.filter(
        Booking.property_id == property_id,
        Booking.status.in_(['confirmed', 'pending']),  # On considère les réservations en attente aussi
        or_(
            # La date de début est dans une période réservée
            and_(
                Booking.start_date <= start_date,
                Booking.end_date > start_date
            ),
            # La date de fin est dans une période réservée
            and_(
                Booking.start_date < end_date,
                Booking.end_date >= end_date
            ),
            # La période de réservation englobe complètement une autre réservation
            and_(
                Booking.start_date >= start_date,
                Booking.end_date <= end_date
            )
        )
    ).count()
    
    return overlapping_bookings == 0

@properties.route('/booking/<int:booking_id>')
@login_required
def booking_details(booking_id):
    """Affiche les détails d'une réservation"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Vérifier que l'utilisateur est autorisé à voir cette réservation
    if booking.user_id != current_user.id and booking.property.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    return render_template('properties/booking_details.html', booking=booking)

@properties.route('/my-bookings')
@login_required
def my_bookings():
    """Affiche la liste des réservations de l'utilisateur"""
    # Récupérer les réservations de l'utilisateur triées par date de création décroissante
    bookings = (Booking.query
                .filter_by(user_id=current_user.id)
                .order_by(Booking.created_at.desc())
                .all())
    
    return render_template('properties/my_bookings.html', bookings=bookings)

@properties.route('/host/bookings')
@login_required
def host_bookings():
    """Affiche la liste des réservations pour les propriétés de l'utilisateur"""
    # Récupérer les propriétés de l'utilisateur
    properties = Property.query.filter_by(user_id=current_user.id).all()
    property_ids = [p.id for p in properties]
    
    # Récupérer les réservations pour ces propriétés
    bookings = (Booking.query
                .filter(Booking.property_id.in_(property_ids))
                .order_by(Booking.created_at.desc())
                .all())
    
    return render_template('properties/host_bookings.html', bookings=bookings)

@properties.route('/booking/<int:booking_id>/update-status', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    """Met à jour le statut d'une réservation (confirmée, annulée, etc.)"""
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    
    # Vérifier que l'utilisateur est autorisé à modifier cette réservation
    if booking.property.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Vérifier que le statut est valide
    if new_status not in ['confirmed', 'cancelled', 'completed']:
        flash('Statut invalide.', 'danger')
        return redirect(request.referrer or url_for('properties.host_bookings'))
    
    # Mettre à jour le statut
    booking.status = new_status
    booking.updated_at = datetime.utcnow()
    
    # Si la réservation est annulée, libérer les dates
    if new_status == 'cancelled':
        # Envoyer une notification à l'utilisateur
        pass  # TODO: Implémenter la notification
    
    db.session.commit()
    
    flash(f'Le statut de la réservation a été mis à jour: {new_status}.', 'success')
    return redirect(request.referrer or url_for('properties.host_bookings'))

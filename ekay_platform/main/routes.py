from flask import render_template, redirect, url_for, request, current_app, flash, abort
from flask_login import current_user, login_required
from . import main
from ..extensions import db
from ..models import User, Property, PropertyImage
from .forms import SearchForm
from datetime import datetime

@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@main.route('/')
@main.route('/index')
def index():
    """Home page with property listings"""
    page = request.args.get('page', 1, type=int)
    query = Property.query.filter_by(is_available=True)
    
    # Apply filters if any
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    rooms = request.args.get('rooms', type=int)
    
    if min_price is not None:
        query = query.filter(Property.price >= min_price)
    if max_price is not None:
        query = query.filter(Property.price <= max_price)
    if rooms is not None:
        query = query.filter(Property.rooms >= rooms)
    
    # Paginate results
    properties = query.order_by(Property.created_at.desc()).paginate(
        page=page, per_page=current_app.config['PROPERTIES_PER_PAGE'], error_out=False)
    
    # Prepare filter form
    form = SearchForm()
    if request.args:
        form.min_price.data = min_price
        form.max_price.data = max_price
        form.rooms.data = rooms
    
    return render_template('main/index.html', 
                         title='Accueil',
                         properties=properties,
                         form=form)

@main.route('/property/<int:id>')
def property(id):
    """Property detail page"""
    property = Property.query.get_or_404(id)
    return render_template('properties/detail.html', 
                         property=property,
                         title=property.title)

@main.route('/search')
def search():
    """Advanced property search"""
    form = SearchForm()
    if form.validate_on_submit():
        # Process search form submission
        min_price = form.min_price.data
        max_price = form.max_price.data
        rooms = form.rooms.data
        
        # Build query based on form data
        query = Property.query.filter_by(is_available=True)
        
        if min_price:
            query = query.filter(Property.price >= min_price)
        if max_price:
            query = query.filter(Property.price <= max_price)
        if rooms:
            query = query.filter(Property.rooms >= rooms)
        
        properties = query.order_by(Property.price).all()
        return render_template('main/search.html', 
                             title='Résultats de recherche',
                             properties=properties,
                             form=form)
    
    # If it's a GET request or form not validated
    return render_template('main/search.html', 
                         title='Recherche avancée',
                         properties=[],
                         form=form)

@main.route('/about')
def about():
    """About page"""
    return render_template('main/about.html', title='À propos')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # Process contact form
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Here you would typically send an email
        flash('Votre message a été envoyé avec succès!', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('main/contact.html', title='Contact')

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.is_landlord:
        # Landlord dashboard
        properties = current_user.properties.order_by(Property.created_at.desc()).all()
        return render_template('dashboard/landlord.html', 
                             title='Tableau de bord Propriétaire',
                             properties=properties)
    else:
        # Tenant dashboard
        favorites = current_user.favorites.all()
        return render_template('dashboard/tenant.html',
                             title='Tableau de bord Locataire',
                             favorites=favorites)

@main.route('/favorite/<int:property_id>', methods=['POST'])
@login_required
def favorite(property_id):
    """Add/remove property from favorites"""
    property = Property.query.get_or_404(property_id)
    
    if property in current_user.favorites:
        current_user.favorites.remove(property)
        db.session.commit()
        return jsonify({'status': 'removed'})
    else:
        current_user.favorites.append(property)
        db.session.commit()
        return jsonify({'status': 'added'})

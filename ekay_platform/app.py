from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from main.forms import PropertyForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_tres_longue_et_aleatoire_ici'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ekay.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload folder exists
os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone_country = db.Column(db.String(2), default='HT')  # Code pays ISO 3166-1 alpha-2
    phone = db.Column(db.String(20))
    phone_prefix = db.Column(db.String(5), default='+509')  # Préfixe téléphonique
    is_landlord = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_full_phone(self):
        """Retourne le numéro de téléphone complet avec le préfixe"""
        if self.phone:
            return f"{self.phone_prefix}{self.phone.lstrip('0')}"
        return ""

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False, comment='Prix mensuel')
    annual_price = db.Column(db.Float, comment='Prix annuel (optionnel)')
    rooms = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(300), nullable=False)
    corridor = db.Column(db.String(50))
    latitude = db.Column(db.Float, default=19.6917)  # Coordonnées par défaut pour Caracol
    longitude = db.Column(db.Float, default=-71.8250)
    village = db.Column(db.String(100), default='La Différence, Caracol')
    color = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('properties', lazy=True))
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade='all, delete-orphan')

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    properties = Property.query.order_by(Property.created_at.desc()).limit(4).all()
    return render_template('index.html', title='Accueil', properties=properties)

@app.route('/api/properties')
def api_properties():
    """API endpoint pour récupérer la liste des propriétés au format JSON"""
    properties = Property.query.all()
    properties_data = []
    
    for prop in properties:
        prop_data = {
            'id': prop.id,
            'title': prop.title,
            'description': prop.description,
            'price': prop.price,
            'annual_price': prop.annual_price,
            'rooms': prop.rooms,
            'address': prop.address,
            'corridor': prop.corridor,
            'village': prop.village,
            'latitude': prop.latitude,
            'longitude': prop.longitude,
            'is_available': prop.is_available,
            'image_url': url_for('static', filename='uploads/' + prop.images[0].filename) if prop.images else url_for('static', filename='images/no-image.jpg')
        }
        properties_data.append(prop_data)
    
    return jsonify(properties_data)

@app.route('/properties')
def properties():
    properties = Property.query.all()
    return render_template('properties/list.html', properties=properties, title='Nos biens')

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('properties/detail.html', property=property)


@app.route('/property/edit/<int:property_id>', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    property = Property.query.get_or_404(property_id)
    
    # Vérifier que l'utilisateur est le propriétaire du bien ou un administrateur
    if property.user_id != current_user.id and not current_user.is_admin:
        flash('Vous n\'êtes pas autorisé à modifier ce bien', 'danger')
        return redirect(url_for('property_detail', property_id=property_id))
    
    form = PropertyForm(obj=property)
    
    if form.validate_on_submit():
        # Mettre à jour les propriétés du bien
        property.title = form.title.data
        property.description = form.description.data
        property.price = float(form.price.data)
        property.annual_price = float(form.annual_price.data) if form.annual_price.data else None
        property.rooms = int(form.rooms.data)
        property.address = form.address.data
        property.corridor = form.corridor.data
        property.color = form.color.data
        property.village = form.village.data or 'La Différence, Caracol'
        property.latitude = float(form.latitude.data) if form.latitude.data else 19.6917
        property.longitude = float(form.longitude.data) if form.longitude.data else -71.8250
        property.is_available = form.is_available.data
        property.updated_at = datetime.utcnow()
        
        # Gérer la suppression des images existantes
        if 'deleted_images' in request.form:
            deleted_ids = request.form.getlist('deleted_images')
            for image_id in deleted_ids:
                image = PropertyImage.query.get(image_id)
                if image and image.property_id == property.id:
                    # Supprimer le fichier physique
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
                    except OSError:
                        pass
                    db.session.delete(image)
        
        # Gérer l'ajout de nouvelles images
        if 'images' in request.files:
            for file in request.files.getlist('images'):
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    image = PropertyImage(filename=filename, property_id=property.id)
                    db.session.add(image)
        
        db.session.commit()
        flash('Bien mis à jour avec succès !', 'success')
        return redirect(url_for('property_detail', property_id=property.id))
    
    # Pré-remplir le formulaire avec les données actuelles
    if not form.latitude.data:
        form.latitude.data = property.latitude or 19.6917
    if not form.longitude.data:
        form.longitude.data = property.longitude or -71.8250
    
    return render_template('properties/form.html', form=form, property=property)


@app.route('/property/delete/<int:property_id>', methods=['POST'])
@login_required
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    
    # Vérifier que l'utilisateur est le propriétaire du bien ou un administrateur
    if property.user_id != current_user.id and not current_user.is_admin:
        flash('Vous n\'êtes pas autorisé à supprimer ce bien', 'danger')
        return redirect(url_for('property_detail', property_id=property_id))
    
    try:
        # Supprimer les images associées
        for image in property.images:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            except OSError:
                pass
            db.session.delete(image)
        
        # Supprimer le bien
        db.session.delete(property)
        db.session.commit()
        
        flash('Bien supprimé avec succès', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        flash('Une erreur est survenue lors de la suppression du bien', 'danger')
        return redirect(url_for('property_detail', property_id=property_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        phone_country = request.form.get('phone_country', 'HT')
        phone_prefix = request.form.get('phone_prefix', '+509')
        is_landlord = 'is_landlord' in request.form
        
        # Nettoyer le numéro de téléphone (supprimer le préfixe s'il est inclus)
        if phone and phone_prefix and phone.startswith(phone_prefix):
            phone = phone[len(phone_prefix):].strip()
        
        # Valider les entrées
        if not all([username, email, password, phone]):
            flash('Veuillez remplir tous les champs obligatoires', 'danger')
            return redirect(url_for('register'))
            
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Un utilisateur avec ce nom d\'utilisateur ou cette adresse email existe déjà', 'danger')
            return redirect(url_for('register'))
            
        # Créer un nouvel utilisateur
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password, method='sha256'),
            phone=phone,
            phone_country=phone_country,
            phone_prefix=phone_prefix,
            is_landlord=is_landlord
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
        
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('login'))
            
        login_user(user, remember=remember)
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_landlord:
        properties = Property.query.filter_by(user_id=current_user.id).all()
        return render_template('landlord_dashboard.html', properties=properties)
    else:
        return render_template('tenant_dashboard.html')

@app.route('/property/new', methods=['GET', 'POST'])
@login_required
def new_property():
    if not current_user.is_landlord:
        flash('Seuls les propriétaires peuvent ajouter des biens', 'danger')
        return redirect(url_for('dashboard'))
    
    form = PropertyForm()
    
    if form.validate_on_submit():
        # Create new property
        property = Property(
            title=form.title.data,
            description=form.description.data,
            price=float(form.price.data),
            annual_price=float(form.annual_price.data) if form.annual_price.data else None,
            rooms=int(form.rooms.data),
            address=form.address.data,
            corridor=form.corridor.data,
            color=form.color.data,
            village=form.village.data or 'La Différence, Caracol',
            latitude=float(form.latitude.data) if form.latitude.data else 19.6917,
            longitude=float(form.longitude.data) if form.longitude.data else -71.8250,
            is_available=form.is_available.data,
            user_id=current_user.id
        )
        
        db.session.add(property)
        db.session.commit()
        
        # Handle file uploads
        if 'images' in request.files:
            for file in request.files.getlist('images'):
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    image = PropertyImage(filename=filename, property_id=property.id)
                    db.session.add(image)
            
            db.session.commit()
        
        flash('Bien ajouté avec succès !', 'success')
        return redirect(url_for('dashboard'))
    
    # Set default values for latitude and longitude
    if not form.latitude.data:
        form.latitude.data = 19.6917
    if not form.longitude.data:
        form.longitude.data = -71.8250
    
    return render_template('properties/form.html', form=form, property=None)
        
    return render_template('new_property.html')

@app.route('/a-propos')
def about():
    return render_template('about.html', title='À propos')

@app.route('/licence')
def licence():
    return render_template('licence.html', title='Licence')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/clear-cache')
def clear_cache():
    return render_template('clear_cache.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Démarrer le serveur en mode debug, accessible depuis n'importe quelle adresse IP
    app.run(host='0.0.0.0', port=5000, debug=True)

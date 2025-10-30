from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from . import properties
from ..extensions import db
from ..models import Property, PropertyImage
from .forms import PropertyForm, PropertyImageForm
from werkzeug.utils import secure_filename
import os
from datetime import datetime

@properties.route('/properties')
def list_properties():
    page = request.args.get('page', 1, type=int)
    properties = Property.query.order_by(Property.created_at.desc()).paginate(
        page=page, per_page=current_app.config['PROPERTIES_PER_PAGE'], error_out=False)
    return render_template('properties/list.html', properties=properties)

@properties.route('/properties/<int:id>')
def view_property(id):
    property = Property.query.get_or_404(id)
    return render_template('properties/view.html', property=property)

@properties.route('/properties/new', methods=['GET', 'POST'])
@login_required
def new_property():
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            country=form.country.data,
            property_type=form.property_type.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            area=form.area.data,
            user_id=current_user.id
        )
        db.session.add(property)
        db.session.commit()
        
        # Handle file upload
        if 'images' in request.files:
            for file in request.files.getlist('images'):
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'properties', str(property.id), filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    file.save(filepath)
                    
                    # Create image record
                    image = PropertyImage(
                        filename=filename,
                        property_id=property.id
                    )
                    db.session.add(image)
            db.session.commit()
        
        flash('Property has been created!', 'success')
        return redirect(url_for('properties.view_property', id=property.id))
    
    return render_template('properties/new.html', title='New Property', form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

from app import create_app, db
from models import User, Property, PropertyImage

app = create_app()

with app.app_context():
    # Create all database tables
    db.create_all()
    print("Database tables created successfully!")
    
    # Optional: Create a default admin user if none exists
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            username='admin',
            email='admin@ekam.com',
            password='admin123',  # Change this in production!
            is_admin=True,
            is_landlord=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Created default admin user")
    
    print("Database initialization complete!")

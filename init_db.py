import os
from app import create_app, db
from ekay_platform.models import User, Property, PropertyImage

def create_tables():
    app = create_app()
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    create_tables()

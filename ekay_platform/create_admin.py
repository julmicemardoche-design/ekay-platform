from app import app, db
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if admin user already exists
    from app import User
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        # Create admin user
        admin = User(
            username='admin',
            email='admin@ekam.com',
            password_hash=generate_password_hash('admin123', method='sha256'),
            phone='1234567890',
            is_landlord=True,
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully!')
    else:
        print('Admin user already exists')
        
    # List all users
    users = User.query.all()
    print('\nCurrent users:')
    for user in users:
        print(f"- {user.username} (Admin: {getattr(user, 'is_admin', False)})")

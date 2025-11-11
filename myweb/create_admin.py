from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        hashed_password = generate_password_hash('admin123')
        admin_user = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created successfully')
    else:
        print('Admin user already exists')

from app import db
from app.models.user import User

def create_test_user():
    # Check if test user already exists
    if not User.query.filter_by(username='admin').first():
        user = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        print('Test user created successfully!')
    else:
        print('Test user already exists!') 
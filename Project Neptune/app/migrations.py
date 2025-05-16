from app import create_app, db
from app.models.user import User

def migrate_database():
    app = create_app()
    with app.app_context():
        # Drop existing tables
        db.drop_all()
        
        # Create tables with new schema
        db.create_all()
        
        # Create default admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            status='active',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        print('Database tables created successfully!')
        print('Default admin user created:')
        print('Username: admin')
        print('Password: admin123')

if __name__ == '__main__':
    migrate_database() 
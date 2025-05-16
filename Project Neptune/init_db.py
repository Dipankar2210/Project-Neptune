from app import create_app, db
from app.commands import create_test_user

app = create_app()

with app.app_context():
    db.create_all()
    create_test_user() 
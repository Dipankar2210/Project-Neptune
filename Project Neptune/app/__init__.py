from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_principal import Principal
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from app.config.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
principal = Principal()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set a secret key if not already in your config
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'your-very-secret-key'  # Use a secure, random key in production!

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    principal.init_app(app)
    csrf.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.controllers.auth import auth_bp
    from app.controllers.main import main_bp
    from app.controllers.kpi import kpi_bp
    from app.controllers.admin import admin_bp
    from app.controllers.project import project_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(kpi_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(project_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app 
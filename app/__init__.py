from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from .models import db, User , Product , Order , OrderItem , CartItem
from .routes import main_bp
from dotenv import load_dotenv
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request
import logging

# Load environment variables
load_dotenv()

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)

    try:
        # Configuration
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
        
        # Database configuration - use PostgreSQL for production, SQLite for local dev
        database_url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
        if not database_url:
            # Fallback to SQLite for local development
            database_url = 'sqlite:///order_system.db'
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Mail configuration
        app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
        app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

        app.logger.info("Configuration loaded successfully")
        
    except Exception as e:
        app.logger.error(f"Error loading config: {e}")
        raise e

    try:
        # Initialize extensions
        db.init_app(app)
        mail.init_app(app)
        login_manager.init_app(app)
        
        # Create tables in application context
        with app.app_context():
            try:
                db.create_all()
                app.logger.info("Database tables created successfully")
            except Exception as db_error:
                app.logger.warning(f"Database creation warning: {db_error}")
        
        app.logger.info("Extensions initialized successfully")
        
    except Exception as e:
        app.logger.error(f"Error initializing extensions: {e}")
        raise e

    try:
        # Setup Flask-Admin (optional - disable in production if needed)
        if os.environ.get('FLASK_ENV') != 'production':
            admin = Admin(app, name='Order-System Admin', template_mode='bootstrap4')
            admin.add_view(AdminModelView(User, db.session))
            admin.add_view(AdminModelView(Product, db.session))
            admin.add_view(AdminModelView(Order, db.session))
            admin.add_view(AdminModelView(OrderItem, db.session))
            admin.add_view(AdminModelView(CartItem, db.session))
            app.logger.info("Admin panel setup completed")
        
    except Exception as e:
        app.logger.warning(f"Admin setup warning (non-critical): {e}")

    try:
        # Register blueprints
        app.register_blueprint(main_bp)
        app.logger.info("Blueprint registered successfully")
        
    except Exception as e:
        app.logger.error(f"Error registering blueprint: {e}")
        raise e

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login', next=request.url))

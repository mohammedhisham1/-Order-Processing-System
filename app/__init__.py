from flask import Flask, request
from flask_login import LoginManager
from flask_mail import Mail
from .models import db, User , Product , Order , OrderItem , CartItem
from .routes import main_bp
from dotenv import load_dotenv
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for

load_dotenv()



mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    print("Starting create_app()...")

    app = Flask(__name__)

    try:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-local-only')
        print("✓ SECRET_KEY loaded")
        
        # Use in-memory SQLite for Vercel deployment
        database_url = os.environ.get('SQLALCHEMY_DATABASE_URI')
        if not database_url:
            # Check if we're in a serverless environment (Vercel)
            if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
                # Use in-memory database for serverless
                database_url = 'sqlite:///:memory:'
                print("✓ Using in-memory database for serverless environment")
            else:
                # Use local file database for development
                database_url = 'sqlite:///instance/order_system.db'
                print("✓ Using file database for local development")
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        print("✓ SQLALCHEMY_DATABASE_URI loaded")

        app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'localhost')
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
        app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

        print("✓ Mail config loaded")
    except Exception as e:
        print("✗ Error loading config:", e)
        # Don't raise here, continue with defaults

    try:
        db.init_app(app)
        with app.app_context():
            db.create_all()
            # Seed basic data if using in-memory database
            if 'memory' in app.config['SQLALCHEMY_DATABASE_URI']:
                from .models import Product
                # Add some basic products if none exist
                if Product.query.count() == 0:
                    basic_products = [
                        Product(name='Sample Product 1', price=10.99, stock=50, description='A sample product for testing'),
                        Product(name='Sample Product 2', price=25.50, stock=30, description='Another sample product'),
                    ]
                    for product in basic_products:
                        db.session.add(product)
                    db.session.commit()
                    print("✓ Basic products seeded")
        mail.init_app(app)
        login_manager.init_app(app)
        print("✓ Extensions initialized")
    except Exception as e:
        print("✗ Error initializing extensions:", e)
        # Continue without raising to prevent complete failure

    try:
        admin = Admin(app, name='Order-System Admin', template_mode='bootstrap4')
        admin.add_view(AdminModelView(User, db.session))
        admin.add_view(AdminModelView(Product, db.session))
        admin.add_view(AdminModelView(Order, db.session))
        admin.add_view(AdminModelView(OrderItem, db.session))
        admin.add_view(AdminModelView(CartItem, db.session))
        print("✓ Admin panel setup")
    except Exception as e:
        print("✗ Error setting up admin:", e)
        # Continue without admin panel if it fails

    try:
        app.register_blueprint(main_bp)
        print("✓ Blueprint registered")
    except Exception as e:
        print("✗ Error registering blueprint:", e)
        raise  # This is critical, so we should fail if blueprints don't register

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.errorhandler(500)
    def internal_error(error):
        print(f"500 Error: {error}")
        return "Internal Server Error - Check logs for details", 500

    @app.errorhandler(404)
    def not_found_error(error):
        if request.path == '/favicon.ico':
            return '', 204  # No content for favicon
        return "Page not found", 404

    print("✓ App created successfully")
    return app

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login', next=request.url))

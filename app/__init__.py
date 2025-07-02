from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from .models import db, User , Product , Order , OrderItem , CartItem
from .routes import main_bp
from dotenv import load_dotenv
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

load_dotenv()



mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    print("Starting create_app()...")

    app = Flask(__name__)

    try:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
        print(" SECRET_KEY loaded")
        
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///data.db')
        print(" SQLALCHEMY_DATABASE_URI loaded")

        app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'localhost')
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
        app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

        print(" Mail config loaded")
    except Exception as e:
        print(" Error loading config:", e)

    try:
        db.init_app(app)
        with app.app_context():
            db.create_all()
        mail.init_app(app)
        login_manager.init_app(app)
        print(" Extensions initialized")
    except Exception as e:
        print(" Error initializing extensions:", e)

    try:
        admin = Admin(app, name='Order-System Admin', template_mode='bootstrap4')
        admin.add_view(ModelView(User, db.session))
        admin.add_view(ModelView(Product, db.session))
        admin.add_view(ModelView(Order, db.session))
        admin.add_view(ModelView(OrderItem, db.session))
        admin.add_view(ModelView(CartItem, db.session))
        print(" Admin panel setup")
    except Exception as e:
        print(" Error setting up admin:", e)

    try:
        app.register_blueprint(main_bp)
        print(" Blueprint registered")
    except Exception as e:
        print(" Error registering blueprint:", e)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

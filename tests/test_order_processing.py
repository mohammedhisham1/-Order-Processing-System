import pytest
from app import create_app
from app.models import db, User, Product, CartItem

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        # Add a sample product
        db.session.add(Product(name='Test Product', price=10.0, stock=5, description='Test'))
        db.session.commit()
    with app.test_client() as client:
        yield client

def register(client, username, email, password):
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def test_user_registration_and_login(client):
    rv = register(client, 'user1', 'user1@example.com', 'password')
    assert b'Please check your email to verify your account' in rv.data

    # Manually verify user for test
    with client.application.app_context():
        user = User.query.filter_by(username='user1').first()
        user.is_verified = True
        db.session.commit()

    rv = login(client, 'user1', 'password')
    assert b'Home' in rv.data or b'Products' in rv.data

def test_product_listing(client):
    rv = client.get('/')
    assert b'Test Product' in rv.data

def test_cart_and_checkout(client):
    register(client, 'user2', 'user2@example.com', 'password')
    with client.application.app_context():
        user = User.query.filter_by(username='user2').first()
        user.is_verified = True
        db.session.commit()
    login(client, 'user2', 'password')

    # Add to cart
    rv = client.post('/add_to_cart/1', data={'quantity': 2}, follow_redirects=True)
    assert b'Product added to cart' in rv.data

    # View cart
    rv = client.get('/cart')
    assert b'Test Product' in rv.data

    # Checkout (simulate payment)
    rv = client.post('/checkout', data={
        'wallet_number': '1234567890',
        'payment_details': 'mock'
    }, follow_redirects=True)
    assert b'Order placed' in rv.data or b'Order placed, but failed to send confirmation email' in rv.data 
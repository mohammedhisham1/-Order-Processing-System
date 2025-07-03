from app import create_app
from app.models import db, Product, User

app = create_app()

with app.app_context():
    db.create_all()
    if not Product.query.first():
        products = [
            Product(
                name='Wireless Mouse', price=25.99, stock=20, description='A smooth and responsive wireless mouse.',
                image_url='https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80'
            ),
            Product(
                name='Mechanical Keyboard', price=79.99, stock=15, description='RGB backlit mechanical keyboard.',
                image_url='https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=400&q=80'
            ),
            Product(
                name='USB-C Charger', price=18.50, stock=30, description='Fast charging USB-C wall charger.',
                image_url='https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=400&q=80'
            ),
            Product(
                name='Noise Cancelling Headphones', price=129.99, stock=10, description='Over-ear headphones with active noise cancellation.',
                image_url='https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80'
            ),
            Product(
                name='Webcam 1080p', price=49.99, stock=25, description='Full HD webcam for video calls and streaming.',
                image_url='https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=400&q=80'
            )
        ]
        db.session.add_all(products)
        db.session.commit()
        print('Sample products added!')
    else:
        print('Products already exist. No changes made.')
import logging
from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('order_system.log'),
        logging.StreamHandler()
    ]
)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 
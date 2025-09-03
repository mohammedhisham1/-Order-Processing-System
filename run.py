import logging
from app import create_app
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Console only
)

# Create the Flask app instance
app = create_app()

# This is required for Vercel to detect the WSGI application
# Vercel looks for an 'app' variable in the entry point file
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
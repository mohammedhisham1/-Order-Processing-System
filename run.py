import logging
from app import create_app
import os

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Create the Flask app
app = create_app()

# This is required for Vercel - it needs to find the app variable
# Vercel will use this as the WSGI application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # Production mode for Vercel
    app.logger.setLevel(logging.INFO)
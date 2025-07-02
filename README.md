# Order-System

A simple online order management system built with Flask, featuring product catalog, shopping cart, order processing, mock payment gateway, and order confirmation emails.

## Features
- Product catalog with stock management
- Shopping cart and checkout flow
- Mock payment gateway
- **Order confirmation emails sent to customers after successful purchase**
- User registration and login
- Error handling and flash messages
- Dockerized for easy deployment

## Setup

### 1. Clone the repository
```
git clone https://github.com/mohammedhisham1/Order-Processing-System.git
cd Order-System
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Set up environment variables
Edit `app/__init__.py` and set your email credentials for Flask-Mail:
```
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-email-password'
```

### 4. Initialize the database
```
python seed.py
```

### 5. Run the app
```
python run.py
```
Visit [http://localhost:5000](http://localhost:5000)

## Docker Usage

### 1. Build the Docker image
```
docker build -t order-system-app .
```

### 2. Run the container
```
docker run -p 5000:5000 order-system-app
```

## Customization
- Order confirmation email templates are in `app/templates/order_confirmation_email.*`
- Add more products via the database or admin interface (to be implemented)

## Testing
```
pytest
```

# Order-System

A simple online order management system built with Flask, featuring product catalog, shopping cart, order processing, mock payment gateway, and order confirmation emails.

## Direct project link:
https://order-processing-system-drab.vercel.app/

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
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Edit the `.env` file with your actual values:
- `SECRET_KEY`: Generate a secure random string
- `DATABASE_URL`: For production, use a cloud database (PostgreSQL recommended)
- Email settings for order confirmations

### 4. Initialize the database
```
python seed.py
```

### 5. Run the app
```
python run.py
```
Visit [http://localhost:5001](http://localhost:5001)

## Deployment

### Vercel Deployment

1. **Prepare Environment Variables**:
   - In Vercel dashboard, go to your project settings
   - Add the following environment variables:
     - `SECRET_KEY`: A secure random string
     - `DATABASE_URL`: PostgreSQL connection string (recommended: Vercel Postgres)
     - `FLASK_ENV`: `production`
     - Email settings: `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`, etc.

2. **Database Setup**:
   - **Important**: SQLite doesn't work with Vercel (serverless)
   - Use Vercel Postgres, PlanetScale, or another cloud database
   - Set `DATABASE_URL` to your PostgreSQL connection string

3. **Deploy**:
   ```bash
   vercel --prod
   ```

### Common Vercel Issues & Solutions:

- **500 Errors**: Usually caused by missing environment variables or database connection issues
- **Database**: Make sure to use PostgreSQL, not SQLite
- **Secret Key**: Must be set in Vercel environment variables
- **Admin Panel**: Disabled in production by default (can be enabled by setting `FLASK_ENV=development`)

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

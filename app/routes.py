from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, Product, User, Order, OrderItem, CartItem
from werkzeug.security import generate_password_hash, check_password_hash
from .payment_gateway import process_payment
from .email_utils import send_order_confirmation, send_verification_email
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@main_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    flash('Product added to cart!')
    return redirect(url_for('main.index'))

@main_bp.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    items = []
    total = 0
    for item in cart_items:
        if item.product:
            items.append({'product': item.product, 'quantity': item.quantity, 'subtotal': item.product.price * item.quantity})
            total += item.product.price * item.quantity
    return render_template('cart.html', items=items, total=total)

@main_bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.')
    return redirect(url_for('main.cart'))

@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!')
        return redirect(url_for('main.index'))
    items = []
    total = 0
    for item in cart_items:
        product = item.product
        if not product or product.stock < item.quantity:
            logging.warning(f"User {current_user.id} attempted to order out-of-stock product {item.product_id}.")
            flash(f'Product {product.name if product else item.product_id} is out of stock!')
            return redirect(url_for('main.cart'))
        items.append({'product': product, 'quantity': item.quantity, 'subtotal': product.price * item.quantity})
        total += product.price * item.quantity
    error = None
    if request.method == 'POST':
        wallet_number = request.form.get('wallet_number')
        payment_details = request.form.get('payment_details')
        if not wallet_number or not payment_details:
            error = 'Please enter all payment details.'
        elif len(wallet_number) != 10 or not wallet_number.isdigit():
            error = 'Wallet number must be 10 digits.'
        else:
            payment_success = process_payment(total, current_user, wallet_number, payment_details)
            if payment_success:
                order = Order(user_id=current_user.id, total_amount=total, paid=True)
                db.session.add(order)
                db.session.flush()
                for item in items:
                    order_item = OrderItem(order_id=order.id, product_id=item['product'].id, quantity=item['quantity'], price=item['product'].price)
                    db.session.add(order_item)
                    item['product'].stock -= item['quantity']
                # Clear cart
                CartItem.query.filter_by(user_id=current_user.id).delete()
                db.session.commit()
                logging.info(f"Order {order.id} placed by user {current_user.id} for ${total}.")
                email_sent = send_order_confirmation(current_user.email, order)
                if not email_sent:
                    logging.error(f"Order {order.id}: Failed to send confirmation email to {current_user.email}.")
                    flash('Order placed, but failed to send confirmation email. Please contact support.', 'warning')
                else:
                    flash('Order placed successfully!')
                return redirect(url_for('main.order_confirmation', order_id=order.id))
            else:
                logging.warning(f"Payment failed for user {current_user.id} during checkout.")
                error = 'Payment failed! Please check your details.'
    return render_template('checkout.html', items=items, total=total, error=error)

@main_bp.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_confirmation.html', order=order)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('main.login'))
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid credentials!')
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists!')
            return redirect(url_for('main.register'))
        user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        send_verification_email(user)
        flash('Registration successful! Please check your email to verify your account.')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main_bp.route('/verify_email/<token>')
def verify_email(token):
    user = User.verify_verification_token(token)
    if not user:
        flash('Verification link is invalid or has expired.', 'danger')
        return redirect(url_for('main.login'))
    if user.is_verified:
        flash('Account already verified. Please log in.', 'info')
    else:
        user.is_verified = True
        db.session.commit()
        flash('Your account has been verified! You can now log in.', 'success')
    return redirect(url_for('main.login'))

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Global error handler for 500 errors
@main_bp.app_errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {error}")
    return render_template('500.html'), 500 
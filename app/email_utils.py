import logging
from flask_mail import Message
from flask import render_template, current_app, url_for

def send_order_confirmation(user_email, order):
    from . import mail  # Import here to avoid circular import
    try:
        msg = Message('Order Confirmation', recipients=[user_email])
        msg.body = render_template('order_confirmation_email.txt', order=order)
        msg.html = render_template('order_confirmation_email.html', order=order)
        mail.send(msg)
        return True
    except Exception as e:
        logging.error(f"Failed to send order confirmation email: {e}")
        return False

def send_verification_email(user):
    from . import mail
    token = user.get_verification_token()
    verify_url = url_for('main.verify_email', token=token, _external=True)
    try:
        msg = Message('Verify Your Email', recipients=[user.email])
        msg.body = render_template('verify_email.txt', user=user, verify_url=verify_url)
        msg.html = render_template('verify_email.html', user=user, verify_url=verify_url)
        mail.send(msg)
        return True
    except Exception as e:
        logging.error(f"Failed to send verification email: {e}")
        return False 
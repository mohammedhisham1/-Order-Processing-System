import random

def process_payment(amount, user, wallet_number, payment_details):
    # Simulate payment processing: succeed if wallet_number is 10 digits and payment_details is not empty
    if len(wallet_number) == 10 and wallet_number.isdigit() and payment_details:
        return random.choice([True, True, True, False])  # 75% chance of success
    return False 
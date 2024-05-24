import random
from .models import db, User, Vendor, Service, Booking, Visit, Receipt, Cashback, Review


def generate_unique_card_number():
    unique = False
    while not unique:
        card_number = random.randint(1000, 9999)
        # Check if this card number already exists
        existing_user = db.session.query(User).filter_by(card_number=card_number).first()
        if not existing_user:
            unique = True
    return card_number

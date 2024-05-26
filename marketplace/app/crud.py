from .models import db, User, Vendor, Service, Booking, Visit, Receipt, Cashback, Review


def create_user(data):
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user


def create_vendor(data):
    vendor = Vendor(**data)
    db.session.add(vendor)
    db.session.commit()
    return vendor


def create_service(data):
    service = Service(**data)
    db.session.add(service)
    db.session.commit()
    return service


# Similarly, add CRUD functions for Services, Bookings, Visits, Receipts, Cashbacks, Reviews

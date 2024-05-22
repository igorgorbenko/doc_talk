from . import ma
from .models import User, Vendor, Service, Booking, Visit, Receipt, Cashback, Review

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class VendorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vendor
        load_instance = True

class ServiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service
        load_instance = True

class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        load_instance = True

class VisitSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Visit
        load_instance = True

class ReceiptSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Receipt
        load_instance = True

class CashbackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cashback
        load_instance = True

class ReviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Review
        load_instance = True

from . import ma
from marshmallow_enum import EnumField
from .models import User, Vendor, Service, Booking, Visit, Receipt, Cashback, Review, UserType, VendorType


class UserSchema(ma.SQLAlchemyAutoSchema):
    # user_type = EnumField(UserType, by_value=True, load_only=True)  # Specifies handling of the UserType enum
    user_type = EnumField(UserType, by_value=True, dump_only=True)  # Changed to dump_only

    class Meta:
        model = User
        load_instance = True
        include_fk = True  # If you have foreign keys and want to include them
        dump_only = ("user_id",)  # Fields that should only be included in responses, not in requests

class VendorSchema(ma.SQLAlchemyAutoSchema):
    vendor_type = EnumField(VendorType, by_value=True, dump_only=True)  # Changed to dump_only

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

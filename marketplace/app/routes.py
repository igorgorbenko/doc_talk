from flask import Blueprint, request, jsonify, render_template
from .models import db, User, Vendor, Service, Booking, Visit, Receipt, Cashback, Review
from .schemas import UserSchema, VendorSchema, ServiceSchema, BookingSchema, VisitSchema, ReceiptSchema, CashbackSchema, ReviewSchema
from .crud import create_user, create_vendor

bp = Blueprint('routes', __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

vendor_schema = VendorSchema()
vendors_schema = VendorSchema(many=True)

service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

visit_schema = VisitSchema()
visits_schema = VisitSchema(many=True)

receipt_schema = ReceiptSchema()
receipts_schema = ReceiptSchema(many=True)

cashback_schema = CashbackSchema()
cashbacks_schema = CashbackSchema(many=True)

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/users', methods=['POST'])
def add_user():
    data = request.json
    new_user = create_user(data)
    print(new_user)
    return user_schema.jsonify(new_user)

@bp.route('/vendors', methods=['POST'])
def add_vendor():
    data = request.json
    new_vendor = create_vendor(data)
    return vendor_schema.jsonify(new_vendor)

# Similarly, add routes for Services, Bookings, Visits, Receipts, Cashbacks, Reviews

def register_routes(app):
    app.register_blueprint(bp)

import os
import logging
from flask import Blueprint, request, jsonify, render_template
from sqlalchemy.exc import SQLAlchemyError

from .models import db, User, Vendor, Service, Booking, Visit, Receipt, Cashback, Review
from .schemas import UserSchema, VendorSchema, ServiceSchema, BookingSchema, VisitSchema, ReceiptSchema, CashbackSchema, ReviewSchema
from .crud import create_user, create_vendor

bp = Blueprint('routes', __name__)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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



# @bp.route('/resources')
# def list_resources():
#     # Путь к папке со статическими файлами
#     static_folder = bp.static_folder
#     # Получение списка всех файлов в этой папке
#     resources = os.listdir(static_folder)
#     return jsonify(resources)
#

@bp.route('/')
def home():
    return render_template('admin.html')

@bp.route('/view_user')
def view_user():
    return render_template('add_user.html')

@bp.route('/view_vendor')
def view_vendor():
    return render_template('add_vendor.html')


@bp.route('/add_user', methods=['POST'])
def add_user():
    try:
        data = request.json
        new_user = create_user(data)
        return user_schema.jsonify(new_user)
    except KeyError as e:
        logging.error(f"Missing data for key {e}")
        return jsonify({'error': f'Missing data for key: {e}'}), 400
    except ValueError as e:
        logging.error(f"Value error: {e}")
        return jsonify({'error': str(e)}), 422
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        return jsonify({'error': 'Database error, please try again later.'}), 500
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/add_vendor', methods=['POST'])
def add_vendor():
    try:
        data = request.json
        new_vendor = create_vendor(data)
        return vendor_schema.jsonify(new_vendor)
    except KeyError as e:
        logging.error(f"Missing data for key {e}")
        return jsonify({'error': f'Missing data for key: {e}'}), 400
    except ValueError as e:
        logging.error(f"Value error: {e}")
        return jsonify({'error': str(e)}), 422
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        return jsonify({'error': 'Database error, please try again later.'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@bp.route('/get_users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return users_schema.jsonify(users)
    except Exception as e:
        logging.error(f"Error retrieving Users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/get_vendors', methods=['GET'])
def get_vendors():
    try:
        vendors = Vendor.query.all()
        return vendors_schema.jsonify(vendors)
    except Exception as e:
        logging.error(f"Error retrieving vendors: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Similarly, add routes for Services, Bookings, Visits, Receipts, Cashbacks, Reviews

def register_routes(app):
    app.register_blueprint(bp)

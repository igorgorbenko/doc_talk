import os
import logging
import json
from datetime import datetime as dt
import requests

from flask import Blueprint, request, jsonify, render_template
from flask import current_app

from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError

from .models import db, User, Vendor, Service, Booking, Visit, Receipt, Cashback, Review
from .schemas import UserSchema, VendorSchema, ServiceSchema, BookingSchema, VisitSchema, ReceiptSchema, CashbackSchema, ReviewSchema
from .crud import create_user, create_vendor

# from telegram import Bot

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# bot = Bot(token=TELEGRAM_BOT_TOKEN)


bp = Blueprint('routes', __name__)
# bp.config['UPLOAD_FOLDER'] = '/path/to/upload'

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



@bp.route('/resources')
def list_resources():
    # Путь к папке со статическими файлами
    static_folder = bp.static_folder
    # Получение списка всех файлов в этой папке
    resources = os.listdir(static_folder)
    return jsonify(resources)

@bp.route('/')
def home():
    return render_template('admin.html')

@bp.route('/view_user')
def view_user():
    return render_template('add_user.html')

@bp.route('/view_vendor')
def view_vendor():
    return render_template('add_vendor.html')

@bp.route('/view_item')
def view_item():
    return render_template('add_item.html')

@bp.route('/view_my_chashback')
def view_my_cashback():
    return render_template('user_dashboard.html')


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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@bp.route('/add_service', methods=['POST'])
def add_service():
    vendor_id = request.form.get('vendor_id')
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    file = request.files.get('fileUpload')
    image_url = None  # Значение по умолчанию для URL изображения

    # Проверяем, что файл существует, и он допустим для загрузки
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        image_url = upload_path  # Сохраняем путь к изображению

    # Создаем новую услугу, даже если изображение не предоставлено
    new_service = Service(
        vendor_id=vendor_id,
        name=name,
        description=description,
        price=None,
        image_url=image_url  # Может быть None, если изображение не загружено
    )
    db.session.add(new_service)
    db.session.commit()

    response_message = {
        'message': 'Service created successfully!',
        'image_url': image_url or "No image provided"
    }
    return jsonify(response_message), 200


@bp.route('/add_booking', methods=['POST'])
def add_booking():
    data = request.json
    tg_id = data.get('tg_id')
    service_id = data.get('service_id')
    booking_date_str = data.get('booking_date_time')

    if not tg_id or not service_id or not booking_date_str:
        return jsonify({"error": "Missing required fields"}), 400
    try:
        booking_date = dt.strptime(booking_date_str, "%Y-%m-%d %H:%M")

        # Поиск пользователя по tg_id
        user = User.query.filter_by(tg_id=tg_id).first()
        if not user:
            return jsonify({"error": f"No user found with tg_id: {tg_id}"}), 404

        # Создание новой записи бронирования
        new_booking = Booking(
            user_id=user.user_id,
            service_id=service_id,
            booking_date=booking_date,
            status='Pending'
        )

        # Добавление записи в сессию и сохранение изменений
        db.session.add(new_booking)
        db.session.commit()
        return jsonify({"message": "Booking successfully added", "booking_id": new_booking.booking_id}), 201

    except Exception as e:
        # В случае ошибки откат изменений и вывод сообщения об ошибке
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    # finally:
    #     # Закрытие сессии
    #     db.session.close()


@bp.route('/get_users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return users_schema.jsonify(users)
    except Exception as e:
        logging.error(f"Error retrieving Users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    existing_user = User.query.filter_by(tg_id=data['tg_id']).first()
    if not existing_user:
        new_user = User(tg_id=data['tg_id'],
                        tg_username=data['tg_username'],
                        tg_first_name=data['tg_first_name'],
                        tg_last_name=data['tg_last_name'],
                        user_type='User')
        db.session.add(new_user)
        db.session.commit()
        return user_schema.jsonify(new_user), 201
    return user_schema.jsonify(existing_user), 200


@bp.route('/check_vendor_by_user', methods=['POST'])
def check_vendor_by_user():
    data = request.json
    existing_user = User.query.filter_by(tg_id=data['tg_id']).first()
    return user_schema.jsonify(existing_user), 200


@bp.route('/get_vendors', methods=['GET'])
def get_vendors():
    try:
        vendor_type = request.args.get('vendor_type')
        if vendor_type:
            vendors = Vendor.query.filter_by(vendor_type=vendor_type).all()
        else:
            vendors = Vendor.query.all()

        return vendors_schema.jsonify(vendors)
    except Exception as e:
        logging.error(f"Error retrieving vendors: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/get_services', methods=['GET'])
def get_services():
    try:
        vendor_id = request.args.get('vendor_id')
        query = db.session.query(Service.service_id,
                                 Service.vendor_id,
                                 Service.name,
                                 Service.description,
                                 Service.price,
                                 Vendor.name.label("vendor_name"),
                                 Service.image_url).join(Vendor)

        if vendor_id:
            query = query.filter(Service.vendor_id == vendor_id)

        services = query.all()

        return jsonify([{
            'service_id': service.service_id,
            'name': service.name,
            'description': service.description,
            'price': float(service.price) if service.price is not None else 0.0,
            'vendor_name': service.vendor_name,
            'image_url': service.image_url
        } for service in services])
    except Exception as e:
        logging.error(f"Error retrieving services: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/notify_vendor', methods=['POST'])
def notify_vendor():
    data = request.json
    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({"error": "Missing booking_id"}), 400

    booking = Booking.query.filter_by(booking_id=booking_id).first()

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    service = Service.query.filter_by(service_id=booking.service_id).first()

    if not service:
        return jsonify({"error": "Service not found"}), 404

    vendor_users = User.query.filter_by(vendor_id=service.vendor_id, user_type='Vendor').all()

    if not vendor_users:
        return jsonify({"error": "No vendor users found"}), 404

    message_text = (f"New booking request:\n"
                    f"Date: {booking.booking_date}\n")

    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "Подтвердить бронирование", "callback_data": f"confirm_{booking_id}"},
                {"text": "Отказать", "callback_data": f"reject_{booking_id}"}
            ]
        ]
    }

    for user in vendor_users:
        chat_id = user.tg_id
        try:
            payload = {
                'chat_id': chat_id,
                'text': message_text,
                'reply_markup': json.dumps(inline_keyboard)
            }
            response = requests.post(TELEGRAM_API_URL, json=payload)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('ok'):
                logging.info(f"Notification sent to user {user.tg_username} (chat_id: {chat_id})")
            else:
                logging.error(
                    f"Failed to send message to user {user.tg_username} (chat_id: {chat_id}): {response_data}")

        except Exception as e:
            logging.error(f"Failed to send message to user {user.tg_username} (chat_id: {chat_id}): {e}")
    return jsonify({"status": "Notifications sent"}), 200
# Similarly, add routes for Services, Bookings, Visits, Receipts, Cashbacks, Reviews


def register_routes(app):
    app.register_blueprint(bp)

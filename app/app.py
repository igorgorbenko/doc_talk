from flask import Flask, request, jsonify
import psycopg2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

# Конфигурация подключения к базе данных
DB_HOST = "127.0.0.0"
DB_NAME = "proton"
DB_USER = "admin"
DB_PASS = "admin"


# Функция для подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

# Функция для создания клиента Google Calendar API
def get_calendar_service():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    return service

@app.route('/save_contact', methods=['POST'])
def save_contact():
    user_id = request.json['user_id']
    phone_number = request.json['phone_number']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO contacts (user_id, phone_number) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET phone_number = EXCLUDED.phone_number", (user_id, phone_number))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "success"}), 200

@app.route('/doctor_schedule', methods=['GET'])
def get_doctor_schedule():
    doctor_id = request.args.get('doctor_id')
    # Здесь нужно интегрировать логику для получения расписания доктора из Google Calendar
    return jsonify({"status": "success", "schedule": []}), 200

@app.route('/create_appointment', methods=['POST'])
def create_appointment():
    user_id = request.json['user_id']
    doctor_id = request.json['doctor_id']
    appointment_time = request.json['appointment_time']
    # Запись в БД и Google Calendar
    return jsonify({"status": "success"}), 200

@app.route('/upcoming_appointments', methods=['GET'])
def get_upcoming_appointments():
    user_id = request.args.get('user_id')
    # Получение информации из БД и Google Calendar
    return jsonify({"status": "success", "appointments": []}), 200

@app.route('/delete_appointment', methods=['DELETE'])
def delete_appointment():
    appointment_id = request.json['appointment_id']
    # Удаление записи из БД и Google Calendar
    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    app.run(debug=True)

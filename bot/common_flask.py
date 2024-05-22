# import os
# from threading import Thread
# from flask import Flask, send_from_directory, request, jsonify
# from telegram import Update, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup
# from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
#
# TOKEN = ""
#
# app = Flask(__name__)
# webapp_path = os.path.join(os.getcwd(), 'webapp')
#
# @app.route('/')
# def serve_index():
#     return send_from_directory(webapp_path, 'index.html')
#
# @app.route('/<path:path>')
# def serve_file(path):
#     return send_from_directory(webapp_path, path)
#
# @app.route('/order', methods=['POST'])
# def receive_order():
#     order_data = request.json
#     # Обработка данных заказа и отправка в Telegram бот
#     # Например, отправка сообщения в чат бота
#     print(order_data)
#     return jsonify({'status': 'success'}), 200
#
# def run_flask():
#     app.run(host='0.0.0.0', port=5001)
#
# async def launch_web_ui(update: Update, context: CallbackContext) -> None:
#     web_app_url = "https://a73b-2001-8f8-1b2f-a514-60c4-e1d4-82a6-7c52.ngrok-free.app/"
#     kb = [
#         [KeyboardButton(
#             "!!Show me my Web-App!",
#             web_app=WebAppInfo(web_app_url)
#         )]
#     ]
#     await update.message.reply_text("Let's do this...", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
#
#
# async def web_app_data(update: Update, context: CallbackContext):
#     print(update.message.web_app_data.data)
#     data = json.loads(update.message.web_app_data.data)
#     await update.message.reply_text("Your data was:")
#     for result in data:
#         await update.message.reply_text(f"{result['name']}: {result['value']}")
#
#
# def main():
#     application = Application.builder().token(TOKEN).build()
#
#     application.add_handler(CommandHandler('start', launch_web_ui))
#     application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
#
#     # Запуск Flask сервера в отдельном потоке
#     flask_thread = Thread(target=run_flask)
#     flask_thread.start()
#
#     application.run_polling()
#
# if __name__ == '__main__':
#     main()


"""app.py"""
import os
import json
import argparse
import urllib.parse
import time
import hashlib
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters

BOT_TOKEN = "7093994454:AAGDuUb-NF5oNmVLffcbJztQfOsCx5zqynA"


def generate_query_id(user_id):
    # Генерация уникального query_id на основе user_id и текущего времени
    return hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()

def generate_hash(auth_date, user_data_json, bot_token):
    # Генерация хэша на основе auth_date, user_data_json и bot_token
    data_check_string = f"auth_date={auth_date}\n{user_data_json}"
    return hashlib.sha256(f"{data_check_string}{bot_token}".encode()).hexdigest()


async def launch_web_ui(update: Update, context: CallbackContext) -> None:
    print(1213123)
    # Получаем данные пользователя
    user_data = {
        "id": update.effective_user.id,
        "first_name": update.effective_user.first_name,
        "last_name": update.effective_user.last_name,
        "username": update.effective_user.username,
        "language_code": update.effective_user.language_code,
        "is_premium": True,  # или используйте update.effective_user.is_premium, если доступно
        "allows_write_to_pm": True  # или используйте соответствующее поле, если доступно
    }
    # print(user_data)
    # Кодируем данные в формате JSON
    user_data_json = json.dumps(user_data)

    # Кодируем данные для URL
    encoded_user_data = urllib.parse.quote(user_data_json)

    # Формируем URL с параметрами
    # web_app_url = f"https://travel.ucoz.ae/shop/telegram_shop/catalog#tgWebAppData=query_id%3DAAEuhtMZAAAAAC6G0xl5-WZZ%26user%3D{encoded_user_data}%26auth_date%3D1716142883%26hash%3D22dd5386bacaee59b4df79899ccc0969e79bcabd26b2f8ea1c83384af61a31ff"
    web_app_url = f"https://t.me/ai_travel_companion_bot/menu"

    # Создаем кнопку для перехода на WebApp с URL
    kb = [
        [KeyboardButton(
            "Show me my Web-App!",
            web_app=WebAppInfo(web_app_url)
        )]
    ]

    await update.message.reply_text("Let's do this...", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))


    # # Получаем данные пользователя
    # user_data = {
    #     "id": update.effective_user.id,
    #     "first_name": update.effective_user.first_name,
    #     "last_name": update.effective_user.last_name,
    #     "username": update.effective_user.username,
    #     "language_code": update.effective_user.language_code,
    #     "is_premium": True,  # или используйте update.effective_user.is_premium, если доступно
    #     "allows_write_to_pm": True  # или используйте соответствующее поле, если доступно
    # }
    #
    # # Кодируем данные в формате JSON
    # user_data_json = json.dumps(user_data, separators=(',', ':'))
    # encoded_user_data = urllib.parse.quote(user_data_json)
    #
    # # Генерация текущей метки времени для auth_date
    # auth_date = int(time.time())
    #
    # # Генерация уникального query_id
    # query_id = generate_query_id(update.effective_user.id)
    #
    # # Генерация хэша
    # hash_value = generate_hash(auth_date, user_data_json, TOKEN)
    #
    # # Формируем URL с параметрами
    # web_app_url = (
    #     f"https://travel.ucoz.ae/shop/telegram_shop"
    #     f"#tgWebAppData=query_id%3D{query_id}%26user%3D{encoded_user_data}%26auth_date%3D{auth_date}%26hash%3D{hash_value}"
    # )
    #
    # # Создаем кнопку для перехода на WebApp с URL
    # kb = [
    #     [KeyboardButton(
    #         "Show me my Web-App!",
    #         web_app=WebAppInfo(web_app_url)
    #     )]
    # ]
    #
    # await update.message.reply_text("Let's do this...", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))


async def web_app_data(update: Update, context: CallbackContext):
    print(update.message.web_app_data.data)
    # data = json.loads(update.message.web_app_data.data)
    # await update.message.reply_text("Your data was:")
    # for result in data:
    #     await update.message.reply_text(f"{result['name']}: {result['value']}")


if __name__ == '__main__':
    # when we run the script we want to first create the bot from the token:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # and let's set a command listener for /start to trigger our Web UI
    application.add_handler(CommandHandler('start', launch_web_ui))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    # and send the bot on its way!
    print(f"Your bot is listening! Navigate to http://t.me/ to interact with it!")
    application.run_polling()
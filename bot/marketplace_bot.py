"""app.py"""
import os
import json
import argparse
import urllib.parse
import time
import hashlib

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters


parser = argparse.ArgumentParser(description="Запуск Telegram бота с параметрами.")
parser.add_argument('--bot_name', type=str, required=True, help="Имя бота")
parser.add_argument('--config', type=str, required=True, help="Путь к файлу конфигурации JSON")
args = parser.parse_args()

with open(args.config, 'r') as json_file:
    config = json.load(json_file)

if args.bot_name in config:
    bot_config = config[args.bot_name]
else:
    raise ValueError(f"Конфигурация для бота с именем {args.bot_name} не найдена.")

TOKEN = bot_config["TOKEN"]
BOT_USERNAME = args.bot_name
GOOGLE_SHEET_URL = bot_config["GOOGLE_SHEET_URL"]
ASSISTANT_ID = bot_config["ASSISTANT_ID"]
GREETINGS_MESSAGE = bot_config["GREETINGS_MESSAGE"]



def generate_query_id(user_id):
    # Генерация уникального query_id на основе user_id и текущего времени
    return hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()

def generate_hash(auth_date, user_data_json, bot_token):
    # Генерация хэша на основе auth_date, user_data_json и bot_token
    data_check_string = f"auth_date={auth_date}\n{user_data_json}"
    return hashlib.sha256(f"{data_check_string}{bot_token}".encode()).hexdigest()


async def launch_web_ui(update: Update, context: CallbackContext) -> None:
    # print(1213123)
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
    # web_app_url = f"https://travel.ucoz.ae/shop/telegram_shop/catalog#tgWebAppData=query_id%3DAGEuhtMZAAAAAC6G0xl5-WZZ%26user%3D{encoded_user_data}%26auth_date%3D1716142883%26hash%3D22dd5386bacaee59b4df79899ccc0969e79bcabd26b2f8ea1c83384af61a31ff"
    # web_app_url = "https://travel.ucoz.ae/shop/telegram_shop/menu"
    # web_app_url = "https://t.me/SportClothesBot/menu"
    # web_app_url = "https://t.me/ai_travel_companion_bot/menu"
    # web_app_url = "https://t.me/ai_marketplace_bot/menu"
    # web_app_url = "https://aimedved.myshopify.com/collections/all"
    # web_app_url = "https://travel.ucoz.ae/shop/restoran-roga-i-kopyta/telegram_shop"
    # web_app_url = f"https://travel.ucoz.ae/shop/telegram_shop/restoran-roga-i-kopyta#tgWebAppData=query_id%3DAGEuhtMZAAAAAC6G0xl5-WZZ%26user%3D{encoded_user_data}%26auth_date%3D1716142883%26hash%3D22dd5386bacaee59b4df79899ccc0969e79bcabd26b2f8ea1c83384af61a31ff"

    # web_app_url = "https://t.me/ai_marketplace_bot/shop"

    # Создаем кнопку для перехода на WebApp с URL
    kb = [
        [KeyboardButton(
            "Show me my Web-App!",
            web_app=WebAppInfo(web_app_url)
        )]
    ]

    await update.message.reply_text("Let's do this...", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

# WORKSS!!!
# async def launch_web_ui(update: Update, context: CallbackContext) -> None:
#     # web_app_url = "https://t.me/SportClothesBot/menu"
#     web_app_url = "https://t.me/ai_travel_companion_bot/menu"
#     kb = [
#         [InlineKeyboardButton(
#             "Show me my Web-App!",
#             url=web_app_url
#         )]
#     ]
#
#     reply_markup = InlineKeyboardMarkup(kb)
#     await update.message.reply_text("Let's do this...", reply_markup=reply_markup)


async def web_app_data(update: Update, context: CallbackContext):
    print(update.message.web_app_data.data)
    # data = json.loads(update.message.web_app_data.data)
    # await update.message.reply_text("Your data was:")
    # for result in data:
    #     await update.message.reply_text(f"{result['name']}: {result['value']}")


if __name__ == '__main__':
    # when we run the script we want to first create the bot from the token:
    application = ApplicationBuilder().token(TOKEN).build()

    # and let's set a command listener for /start to trigger our Web UI
    application.add_handler(CommandHandler('start', launch_web_ui))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    # and send the bot on its way!
    print(f"Your bot is listening! Navigate to http://t.me/{BOT_USERNAME} to interact with it!")
    application.run_polling()
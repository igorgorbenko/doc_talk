import asyncio
import logging
import os
import re
import base64
import httpx

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters,
                          CallbackQueryHandler, ConversationHandler)
from telegram.constants import ChatAction, ParseMode
import requests

from openai_stuff.openai_stuff import OpenAIAssistant
from openai import OpenAI

TOKEN = ""
BOT_USERNAME = "ai_assist_travel_bot"

ASSISTANT_ID = "asst_84zHfX8FkiPGZaxX2BfAd2cm"
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
ASSISTANT_GPT = OpenAIAssistant(OPENAI_API_KEY, ASSISTANT_ID)

OpenAI.api_key = OPENAI_API_KEY
client = OpenAI()

DATE, TIME, CONFIRM = range(3)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', level=logging.INFO)
# Configure the httpx logger to only output warnings or higher level messages
logging.getLogger("httpx").setLevel(logging.WARNING)


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


async def get_balance(update: Update, context: CallbackContext) -> None:
    kb = [
        [InlineKeyboardButton("Посмотрите свой кэшбек", web_app=WebAppInfo(url="https://gentle-piglet-legal.ngrok-free.app/view_my_chashback"))]
    ]
    reply_markup = InlineKeyboardMarkup(kb)
    await update.message.reply_text("Нажмите на кнопку ниже, чтобы открыть личный кабинет:", reply_markup=reply_markup)


async def shop(update: Update, context: CallbackContext) -> None:
    kb = [
        [InlineKeyboardButton("🛍️ Открыть интернет-магазин с товарами наших партнеров", web_app=WebAppInfo(url="https://travel.ucoz.ae/shop/telegram_shop"))]
    ]
    reply_markup = InlineKeyboardMarkup(kb)
    await update.message.reply_text("Нажмите на кнопку ниже, чтобы открыть магазин:", reply_markup=reply_markup)

# Основное меню
async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user = update.message.from_user
    tg_user_params = {
        'tg_id': user.id,
        'tg_username': user.username,
        'tg_first_name': user.first_name,
        'tg_last_name': user.last_name
    }

    # Получение кешбека из базы данных
    # cashback = get_user_cashback(tg_username)
    cashback = 3250
    # card_number = 1001
    response = requests.post("http://127.0.0.1:8000/register", json=tg_user_params)
    if response.status_code == 201:
        card_number = response.json()['card_number']
        await update.message.reply_text(f'Welcome! Your discount card number is {card_number}.')
    elif response.status_code == 200:
        card_number = response.json()['card_number']
        await update.message.reply_text(f'Welcome back! Your card number is: {card_number}')

    web_app_url = (f"https://gentle-piglet-legal.ngrok-free.app/view_my_chashback"
                   f"?tg_username={tg_user_params['tg_username']}&tg_first_name={tg_user_params['tg_first_name']}"
                   f"&tg_last_name={tg_user_params['tg_last_name']}&cashback={cashback}&card_number={card_number}")

    kb = [
        [KeyboardButton("🎧 Помощь оператора")],
        [KeyboardButton("⁉️ О нашем сервисе"), KeyboardButton("📋 Список партнеров")],
        [KeyboardButton("🍽️ Мои бронирования")],
        [KeyboardButton("💸 Мой кэшбек", web_app=WebAppInfo(url=web_app_url)), KeyboardButton("📷 Загрузить чек")]
    ]
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)

    # # Приветствие при стандартном вызове команды /start
    await update.message.reply_text('Привет! Я консьерж-бот для организации досуга')
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)  # Задержка для имитации печати
    await update.message.reply_text("Пожалуйста, выберите один из вариантов на клавиатуре ниже:", reply_markup=reply_markup)


def clean_response(text):
    cleaned_text = re.sub(r'【\d+:\d+†*】', '', text)
    return cleaned_text.strip()


async def handle_operator(update: Update, context: CallbackContext, user_input: str) -> str:
    chat_id = update.effective_chat.id
    tg_username = update.effective_user.username
    context_thread_id = context.user_data.get('thread')

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    await asyncio.sleep(0.8)

    try:
        logging.info(f'QUESTION: tg_username: {tg_username} - {user_input}')

        if context_thread_id:
            response, _ = ASSISTANT_GPT.fetch_formatted_response(user_input=user_input, thread_id=context_thread_id)
        else:
            response, thread_id = ASSISTANT_GPT.fetch_formatted_response(user_input=user_input)
            context.user_data['thread'] = thread_id

        if not response:
            raise ValueError("Received empty response from ChatGPT")

        cleaned_response = clean_response(response)
        logging.info(f'ANSWER: tg_username: {tg_username} - {cleaned_response}')
        return cleaned_response
    except Exception as e:
        logging.error("Произошла ошибка: " + str(e))
        return "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз."


async def recognize_total_amount(image_path):
    base64_image = encode_image(image_path)

    try:
        with open(image_path, "rb") as image_file:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Найди итоговую сумму чека и выведи результат только эту сумму. "
                                                     "Никакие другие слова не выводи"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=10
            )
        return response.choices[0].message.content
    except httpx.RequestError as e:
        logging.error(f"An error occurred while requesting: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logging.error(f"Error response {e.response.status_code} while requesting {e.request.url}")
        raise
    except Exception as e:
        logging.error(f"Error while the calling the transcribe_audio_with_openai {str(e)}")
        raise


# Обработка загрузки фотографии
async def handle_photo(update: Update, context: CallbackContext) -> None:
    photo_file = await update.message.photo[-1].get_file()
    file_path = os.path.join("/tmp", f"{photo_file.file_id}.jpg")
    await photo_file.download_to_drive(file_path)
    await update.message.reply_text("Фотограция получена, обрабатывается...")

    # Предварительная обработка изображения и распознавание текста
    total_amount = await recognize_total_amount(file_path)

    if total_amount:
        await update.message.reply_text(f"Сумма на чеке: {total_amount} руб.")
    else:
        await update.message.reply_text("Не удалось распознать сумму на чеке. Пожалуйста, попробуйте еще раз.")


# Обработка сообщений от пользователя
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    chat_id = update.message.chat_id

    if user_message == "🎧 Помощь оператора":
        await update.message.reply_text("Связываю вас с оператором...")
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)  # Задержка для имитации печати
        await update.message.reply_text("Оператор на связи, введите свой вопрос")
        context.user_data['awaiting_response'] = True  # Флаг для ожидания ответа пользователя
    elif user_message in ["⁉️ О нашем сервисе", "📋 Список партнеров", "🍽️ Мои бронирования", "💸 Мой кэшбек"]:
        context.user_data['awaiting_response'] = False  # Сбрасываем флаг ожидания ответа
        await handle_predefined_questions(update, context, user_message)
    elif user_message == "📷 Загрузить чек":
        await update.message.reply_text("Пожалуйста, отправьте фото чека.")
    else:
        if context.user_data.get('awaiting_response'):
            response = await handle_operator(update, context, user_message)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Извините, я не понял ваш запрос. Пожалуйста, выберите один из вариантов меню.")


async def handle_query(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    text = query.data

    logging.info(f"Received callback query: {text}")

    if text in ['Hotel', 'Restaurant', 'Yacht', 'TourOperator']:
        logging.info(f"user {update.effective_user.username} selected {text}")

        response = requests.get(f"http://127.0.0.1:8000/get_vendors?vendor_type={text}")
        if response.status_code == 200:
            vendors = response.json()
            context.user_data['vendors'] = vendors
            message, reply_markup = format_vendor_list_with_buttons(vendors)
            await query.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        else:
            logging.error(f"Failed to get vendors: {response.status_code}")
            await query.message.reply_text("Ошибка при получении списка вендоров. Попробуйте позже.")
    elif text.startswith('select_vendor_'):
        vendor_id = int(text.split('_')[2])
        logging.info(f"vendor {vendor_id}")

        response = requests.get(f"http://127.0.0.1:8000/get_services?vendor_id={vendor_id}")
        if response.status_code == 200:
            services = response.json()
            message, reply_markup = get_list_services(services)
            await query.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        else:
            logging.error(f"Failed to get services: {response.status_code}")
            await query.message.reply_text("Ошибка при получении списка услуг. Попробуйте позже.")

    elif text == "back_to_vendors":
        await get_vendors_type_list(update, context, True)
    else:
        logging.error(f"Unknown callback data {text}")
        await query.message.reply_text("Неизвестный запрос.")

# Conversation handler states
async def book_service(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    text = query.data
    context.user_data['service_id'] = int(text.split('_')[2])

    logging.info(f"Entering book_service with callback query: {query.data}")
    await query.message.reply_text("Пожалуйста, введите желаемую дату бронирования (в формате YYYY-MM-DD):")
    return DATE

async def received_date(update: Update, context: CallbackContext):
    logging.info(f"Entering received_date with message: {update.message.text}")
    context.user_data['booking_date'] = update.message.text
    await update.message.reply_text("Пожалуйста, введите желаемое время бронирования (в формате HH:MM):")
    return TIME

async def received_time(update: Update, context: CallbackContext):
    logging.info(f"Entering received_time with message: {update.message.text}")
    context.user_data['booking_time'] = update.message.text
    booking_date = context.user_data['booking_date']
    booking_time = context.user_data['booking_time']

    keyboard = [
        [InlineKeyboardButton("Подтвердить", callback_data='confirm')],
        [InlineKeyboardButton("Отменить", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Вы хотите забронировать на {booking_date} в {booking_time}. Подтвердите бронирование.",
        reply_markup=reply_markup)
    return CONFIRM

async def confirm_booking(update: Update, context: CallbackContext):
    logging.info("Entering confirm_booking")
    query = update.callback_query
    await query.answer()
    booking_date = context.user_data['booking_date']
    booking_time = context.user_data['booking_time']
    tg_user_id = query.from_user.id

    booking_params = {
        'tg_id': tg_user_id,
        'service_id': context.user_data['service_id'],
        'booking_date_time': f"{booking_date} {booking_time}"
    }

    message = f"User {tg_user_id} забронировал столик на {booking_date} в {booking_time}."
    response = requests.post("http://127.0.0.1:8000/add_booking", json=booking_params)
    if response.status_code == 201:
        booking_id = response.json()['booking_id']
        await notify_vendor(message)
        await query.edit_message_text(f"Ваше бронирование на {booking_date} в {booking_time} "
                                      f"отправлено партнеру для подтверждения.")
        return ConversationHandler.END
    else:
        logging.error(f"Error during the booking process! response.status_code: {response.status_code}")
        await query.edit_message_text(f"Не удалось сохранить ваше бронирование! Пожалуйста, повторите операцию позднее")


async def cancel_booking(update: Update, context: CallbackContext):
    logging.info("Entering cancel_booking")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Бронирование отменено.")
    await get_vendors_type_list(update, context, True)
    return ConversationHandler.END

def get_list_services(services):
    keyboard = [[InlineKeyboardButton("Вернуться назад", callback_data="back_to_vendors")]]
    message = "*Список услуг выбранного поставщика:*\n\n"

    for service in services:
        keyboard.insert(0,
                        [InlineKeyboardButton(service['name'], callback_data=f"book_service_{service['service_id']}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return message, reply_markup

def format_vendor_list_with_buttons(vendors):
    keyboard = []
    for vendor in vendors:
        keyboard.append([InlineKeyboardButton(vendor['name'], callback_data=f"select_vendor_{vendor['vendor_id']}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "*Список поставщиков услуг:*\n\n"
    for vendor in vendors:
        message += f"*Название:* {vendor['name']}\n"
        message += f"*Адрес:* {vendor['address']}\n\n"
    return message, reply_markup

async def get_vendors_type_list(update: Update, context: CallbackContext, from_return=False):
    kb = [
        [InlineKeyboardButton("Рестораны", callback_data='Restaurant'),
         InlineKeyboardButton("Отели", callback_data='Hotel')],
        [InlineKeyboardButton("Яхты", callback_data='Yacht'),
         InlineKeyboardButton("Туры и экскурсии", callback_data='TourOperator')]
    ]
    reply_markup = InlineKeyboardMarkup(kb)
    if not from_return:
        await update.message.reply_text("Пожалуйста, выберите интересующую вас категорию партнеров:",
                                        reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text("Пожалуйста, выберите интересующую вас категорию партнеров:",
                                                       reply_markup=reply_markup)

async def handle_predefined_questions(update: Update, context: CallbackContext, question_type: str) -> None:
    if question_type == "⁉️ О нашем сервисе":
        await update.message.reply_text("Здесь будет текст о сервисе...")
    elif question_type == "📋 Список партнеров":
        await get_vendors_type_list(update, context)
    elif question_type == "🍽️ Мои бронирования":
        await get_my_booking_list(update, context)
    elif question_type == "💸 Мой кэшбек":
        await update.message.reply_text("Проверяю ваш баланс...")


async await get_my_booking_list(update, context):
    pass

async def web_app_data(update: Update, context: CallbackContext):
    logging.info(update.message.web_app_data.data)

async def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

async def notify_vendor(message):
    # Logic to notify vendor
    pass


if __name__ == '__main__':
    # Create Telegram application
    application = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('shop', shop))
    application.add_handler(CommandHandler('balance', get_balance))

    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex(r'^\d{4}-\d{2}-\d{2}$') & ~filters.Regex(r'^\d{2}:\d{2}$'),
                                           handle_message))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(book_service, pattern='book_service*')],
        states={
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'^\d{4}-\d{2}-\d{2}$'), received_date)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'^\d{2}:\d{2}$'), received_time)],
            CONFIRM: [CallbackQueryHandler(confirm_booking, pattern='^confirm$'),
                      CallbackQueryHandler(cancel_booking, pattern='^cancel$')]
        },
        fallbacks=[CommandHandler('cancel', cancel_booking)]
    )
    application.add_handler(conv_handler)

    # Callback query handler for other patterns
    application.add_handler(CallbackQueryHandler(handle_query, pattern='^(?!book_service$).*'))

    # Error handler
    application.add_error_handler(error_handler)

    # Start bot
    print(f"Your bot is listening! Navigate to http://t.me/{BOT_USERNAME} to interact with it!")
    application.run_polling()
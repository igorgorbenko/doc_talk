import asyncio
import logging
import os
import re
import base64
import httpx

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters, CallbackQueryHandler
from telegram.constants import ChatAction, ParseMode
import requests

from openai_stuff.openai_stuff import OpenAIAssistant
from openai import OpenAI

TOKEN = ""
BOT_USERNAME = "ai_assist_travel_bot"

ASSISTANT_ID = ""
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
ASSISTANT_GPT = OpenAIAssistant(OPENAI_API_KEY, ASSISTANT_ID)

OpenAI.api_key = OPENAI_API_KEY
client = OpenAI()


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Configure the httpx logger to only output warnings or higher level messages
logging.getLogger("httpx").setLevel(logging.WARNING)


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


async def get_balance(update: Update, context: CallbackContext) -> None:
    kb = [
        # [InlineKeyboardButton("Посмотрите свой кэшбек", web_app=WebAppInfo(url="https://b35d-2001-8f8-1b2f-a514-f83f-7537-cecb-4f8c.ngrok-free.app/user_dashboard.html"))]
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
    print('response.json()', response.json())
    if response.status_code == 201:
        card_number = response.json()['card_number']
        await update.message.reply_text(f'Welcome! Your discount card number is {card_number}.')
    elif response.status_code == 200:
        card_number = response.json()['card_number']
        await update.message.reply_text(f'Welcome back! Your card number is: {card_number}')

    web_app_url = (f"https://gentle-piglet-legal.ngrok-free.app/view_my_chashback"
                   f"?tg_username={tg_user_params['tg_username']}&tg_first_name={tg_user_params['tg_first_name']}"
                   f"&tg_last_name={tg_user_params['tg_last_name']}&cashback={cashback}&card_number={card_number}")

    print(web_app_url)

    kb = [
        [KeyboardButton("🎧 Помощь оператора")],
        [KeyboardButton("⁉️ О нашем сервисе"), KeyboardButton("📋 Список партнеров")],
        [KeyboardButton("🍽️ Забронировать столик")],
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
    elif user_message in ["⁉️ О нашем сервисе", "📋 Список партнеров", "🍽️ Забронировать столик", "💸 Мой кэшбек"]:
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

    if text in ['Hotel', 'Restaurant', 'Yacht', 'TourOperator']:
        logging.info(f"user {update.effective_user.username} selected {text}")

        # Получаем список вендоров по типу
        response = requests.get(f"http://127.0.0.1:8000/get_vendors?vendor_type={text}")
        if response.status_code == 200:
            vendors = response.json()
            context.user_data['vendors'] = vendors  # Сохраняем список вендоров
            message, reply_markup = format_vendor_list_with_buttons(vendors)
            await query.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        else:
            logging.error(f"Failed to get vendors: {response.status_code}")
            await query.message.reply_text("Ошибка при получении списка вендоров. Попробуйте позже.")
    elif text.startswith('book_'):
        vendor_id = int(text.split('_')[1])
        vendors = context.user_data.get('vendors', [])
        vendor = next((v for v in vendors if v['vendor_id'] == vendor_id), None)
        if vendor:
            message, reply_markup = format_vendor_details(vendor)
            await query.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        else:
            await query.message.reply_text("Поставщик не найден.")
    elif text.startswith('book_table_'):
        vendor_id = text.split('_')[2]
        await query.message.reply_text(f"Вы выбрали бронирование столика у поставщика с ID {vendor_id}.")
        # Логика для продолжения процесса бронирования
    elif text == "back_to_vendors":
        # Логика для возврата к списку вендоров
        await get_vendors_type_list(update, context, True)
        # await query.message.reply_text("Пожалуйста, выберите тип поставщика:", reply_markup=InlineKeyboardMarkup([
        #     [InlineKeyboardButton("Hotel", callback_data="Hotel")],
        #     [InlineKeyboardButton("Restaurant", callback_data="Restaurant")],
        #     [InlineKeyboardButton("Yacht", callback_data="Yacht")],
        #     [InlineKeyboardButton("TourOperator", callback_data="TourOperator")],
        # ]))
    else:
        logging.error(f"Unknown callback data {text}")
        await query.message.reply_text("Неизвестный запрос.")

def format_vendor_details(vendor):
    message = f"*Название:* {vendor['name']}\n"
    message += f"*Тип:* {vendor['vendor_type']}\n"
    message += f"*Адрес:* {vendor['address']}\n"
    message += f"*Описание:* {vendor.get('description', 'Описание отсутствует')}\n"

    keyboard = [
        [InlineKeyboardButton("Забронировать стол", callback_data=f"book_table_{vendor['vendor_id']}")],
        [InlineKeyboardButton("Вернуться назад", callback_data="back_to_vendors")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return message, reply_markup


def format_vendor_list_with_buttons(vendors):
    keyboard = []
    for vendor in vendors:
        keyboard.append([InlineKeyboardButton(vendor['name'], callback_data=f"book_{vendor['vendor_id']}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "*Список поставщиков услуг:*\n\n"
    for vendor in vendors:
        message += f"*Название:* {vendor['name']}\n"
        message += f"*Тип:* {vendor['vendor_type']}\n"
        message += f"*Адрес:* {vendor['address']}\n"
        message += "\n"
    return message, reply_markup


async def get_vendors_type_list(update: Update, context: CallbackContext, from_return=False):
    kb = [
        [InlineKeyboardButton("Рестораны", callback_data='Restaurant'), InlineKeyboardButton("Отели", callback_data='Hotel')],
        [InlineKeyboardButton("Яхты", callback_data='Yacht'), InlineKeyboardButton("Туры и экскурсии", callback_data='TourOperator')]
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
    elif question_type == "🍽️ Забронировать столик":
        await update.message.reply_text("Здесь будет реализовано бронирование...")
    elif question_type == "💸 Мой кэшбек":
        await update.message.reply_text("Проверяю ваш баланс...")
        # await get_balance(update, CallbackContext)
        # TODO


async def web_app_data(update: Update, context: CallbackContext):
    logging.info(update.message.web_app_data.data)

async def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)


if __name__ == '__main__':
    # Создание приложения Telegram
    application = ApplicationBuilder().token(TOKEN).build()

    # Настройка командного обработчика /start для запуска основного меню
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('shop', shop))
    application.add_handler(CommandHandler('balance', get_balance))
    # Обработчик сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    # Обработчик InloineKeyboard
    application.add_handler(CallbackQueryHandler(handle_query))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Запуск бота
    print(f"Your bot is listening! Navigate to http://t.me/{BOT_USERNAME} to interact with it!")
    application.run_polling()

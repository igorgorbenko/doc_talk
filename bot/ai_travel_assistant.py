import asyncio
import logging
import os
import re

import pytesseract
from PIL import Image
import cv2

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters
from telegram.constants import ChatAction

from openai_stuff.openai_stuff import OpenAIAssistant

# Установка переменной окружения для Tesseract
os.environ["TESSDATA_PREFIX"] = "/opt/homebrew/share/tessdata/"

TOKEN = ""
BOT_USERNAME = ""
ASSISTANT_ID = ""
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

ASSISTANT_GPT = OpenAIAssistant(OPENAI_API_KEY, ASSISTANT_ID)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Configure the httpx logger to only output warnings or higher level messages
logging.getLogger("httpx").setLevel(logging.WARNING)


async def get_balance(update: Update, context: CallbackContext) -> None:
    kb = [
        [InlineKeyboardButton("Посмотрите свой кэшбек", web_app=WebAppInfo(url="https://b35d-2001-8f8-1b2f-a514-f83f-7537-cecb-4f8c.ngrok-free.app/user_dashboard.html"))]
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
    tg_username = user.username
    tg_first_name = user.first_name
    tg_last_name = user.last_name

    # Получение кешбека из базы данных
    # cashback = get_user_cashback(tg_username)
    cashback = 3250

    web_app_url = (f"https://b35d-2001-8f8-1b2f-a514-f83f-7537-cecb-4f8c.ngrok-free.app/user_dashboard.html"
                   f"?tg_username={tg_username}&tg_first_name={tg_first_name}&tg_last_name={tg_last_name}&cashback={cashback}")

    kb = [
        [KeyboardButton("🎧 Помощь оператора")],
        [KeyboardButton("⁉️ О нашем сервисе"), KeyboardButton("📋 Список партнеров")],
        [KeyboardButton("🍽️ Забронировать столик")],
        [KeyboardButton("💸 Мой кэшбек", web_app=WebAppInfo(url=web_app_url)), KeyboardButton("📷 Загрузить чек")]
    ]
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)

    # Приветствие при стандартном вызове команды /start
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

# Функция предварительной обработки изображения
def preprocess_image(file_path):
    img = cv2.imread(file_path)

    # Конвертация в оттенки серого
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Применение пороговой обработки
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Сохранение обработанного изображения
    processed_image_path = file_path.replace(".jpg", "_processed.jpg")
    cv2.imwrite(processed_image_path, thresh)
    return processed_image_path


# Обработка загрузки фотографии
async def handle_photo(update: Update, context: CallbackContext) -> None:
    photo_file = await update.message.photo[-1].get_file()
    file_path = os.path.join("/tmp", f"{photo_file.file_id}.jpg")
    await photo_file.download_to_drive(file_path)

    # Предварительная обработка изображения и распознавание текста
    processed_image_path = preprocess_image(file_path)
    total_amount = recognize_total_amount(processed_image_path)

    if total_amount:
        await update.message.reply_text(f"Сумма на чеке: {total_amount} руб.")
    else:
        await update.message.reply_text("Не удалось распознать сумму на чеке. Пожалуйста, попробуйте еще раз.")


def recognize_total_amount(file_path):
    # Убедитесь, что TESSDATA_PREFIX правильно настроен
    tessdata_prefix = os.getenv('TESSDATA_PREFIX')
    if tessdata_prefix:
        print(f"TESSDATA_PREFIX is set to: {tessdata_prefix}")
    else:
        print("TESSDATA_PREFIX is not set")

    # Распознавание текста с помощью Tesseract
    text = pytesseract.image_to_string(Image.open(file_path), lang='rus')
    logging.info(f"Распознанный текст: {text}")

    # Поиск строки "Итого к оплате" и суммы
    lines = text.split('\n')
    for line in lines:
        if any(phrase in line.lower() for phrase in ["итого к оплате", "к оплате"]):
            # Извлечение суммы
            amount = extract_amount(line)
            return amount
    return None

def extract_amount(text):
    # Использование регулярного выражения для поиска суммы
    import re
    match = re.search(r'\d+[\.,]?\d*', text)
    if match:
        return match.group().replace(',', '.')
    return None


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


async def handle_predefined_questions(update: Update, context: CallbackContext, question_type: str) -> None:
    if question_type == "⁉️ О нашем сервисе":
        await update.message.reply_text("Здесь будет текст о сервисе...")
    elif question_type == "📋 Список партнеров":
        await update.message.reply_text("Здесь будет список партнеров...")
    elif question_type == "🍽️ Забронировать столик":
        await update.message.reply_text("Здесь будет реализовано бронирование...")
    elif question_type == "💸 Мой кэшбек":
        await update.message.reply_text("Проверяю ваш баланс...")
        # await get_balance(update, CallbackContext)
        # TODO


async def web_app_data(update: Update, context: CallbackContext):
    logging.info(update.message.web_app_data.data)


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

    # Запуск бота
    print(f"Your bot is listening! Navigate to http://t.me/{BOT_USERNAME} to interact with it!")
    application.run_polling()

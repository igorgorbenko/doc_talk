import os
import logging
import argparse
import json
import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler, CallbackContext
import openai

from openai_stuff.openai_stuff import OpenAIAssistant

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
GOOGLE_SHEET_URL = bot_config["GOOGLE_SHEET_URL"]
ASSISTANT_ID = bot_config["ASSISTANT_ID"]
GREETINGS_MESSAGE = bot_config["GREETINGS_MESSAGE"]

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')

ASSISTANT_GPT = OpenAIAssistant(OPENAI_API_KEY, ASSISTANT_ID)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Определение состояний
(ASK_NAME, ASK_CONTACT, ASK_CLINIC, ASK_DOCTOR, ASK_DATE, ASK_QUESTIONS) = range(6)

def clean_response(text):
    cleaned_text = re.sub(r'【\d+:\d+†*】', '', text)
    return cleaned_text.strip()

async def get_response(user_input, update: Update, context: CallbackContext) -> str:
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
    else:
        raise AttributeError("Cannot find chat_id in update")

    tg_username = update.effective_user.username
    context_thread_id = context.user_data.get('thread')

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    await asyncio.sleep(1)

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

# Создание Inline кнопки "Назад"
def back_button_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])

# Обработка кнопки "Назад"
async def back_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    previous_state = context.user_data.get('previous_state')
    previous_question = context.user_data.get('previous_question')

    if previous_state and previous_question:
        current_text = query.message.text
        if current_text != previous_question:
            await query.edit_message_text(previous_question, reply_markup=back_button_markup())
        return previous_state
    else:
        await query.edit_message_text("Не удалось вернуться назад.")
        return ASK_QUESTIONS

# Стартовая функция
async def start(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать запись", callback_data='start_record')],
        [InlineKeyboardButton("Вопросы о врачах", callback_data='doctor_questions')],
        [InlineKeyboardButton("Вопросы о ценах", callback_data='price_questions')],
        [InlineKeyboardButton("Вопросы об услугах", callback_data='service_questions')]
    ])
    await update.message.reply_text("Привет! Как я могу вам помочь?", reply_markup=reply_markup)
    return ASK_QUESTIONS

# Обработка выбора пользователя
async def ask_questions(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    text = query.data

    if text == 'start_record':
        question = "Начнем запись. Как вас зовут?"
        await query.edit_message_text(question, reply_markup=back_button_markup())
        context.user_data['previous_state'] = ASK_QUESTIONS
        context.user_data['previous_question'] = question
        return ASK_NAME
    elif text == 'doctor_questions':
        prompt = "Пользователь хочет узнать о врачах. Дай информацию о врачах."
        response = await get_response(prompt, update, context)
        await query.edit_message_text(response, reply_markup=back_button_markup())
        context.user_data['previous_state'] = ASK_QUESTIONS
        context.user_data['previous_question'] = "Пользователь хочет узнать о врачах. Дай информацию о врачах."
        return ASK_QUESTIONS
    elif text == 'price_questions':
        prompt = "Пользователь хочет узнать о ценах. Дай информацию о ценах."
        response = await get_response(prompt, update, context)
        await query.edit_message_text(response, reply_markup=back_button_markup())
        context.user_data['previous_state'] = ASK_QUESTIONS
        context.user_data['previous_question'] = "Пользователь хочет узнать о ценах. Дай информацию о ценах."
        return ASK_QUESTIONS
    elif text == 'service_questions':
        prompt = "Пользователь хочет узнать об услугах. Дай информацию об услугах."
        response = await get_response(prompt, update, context)
        await query.edit_message_text(response, reply_markup=back_button_markup())
        context.user_data['previous_state'] = ASK_QUESTIONS
        context.user_data['previous_question'] = "Пользователь хочет узнать об услугах. Дай информацию об услугах."
        return ASK_QUESTIONS
    elif text == 'back':
        previous_state = context.user_data.get('previous_state')
        previous_question = context.user_data.get('previous_question')
        if previous_state and previous_question:
            await query.edit_message_text(previous_question, reply_markup=back_button_markup())
            return previous_state
        else:
            await query.edit_message_text("Не удалось вернуться назад.")
            return ASK_QUESTIONS
    else:
        prompt = f"Пользователь задал вопрос: '{text}'. Ответь на вопрос."
        response = await get_response(prompt, update, context)
        await query.edit_message_text(response, reply_markup=back_button_markup())
        context.user_data['previous_state'] = ASK_QUESTIONS
        context.user_data['previous_question'] = f"Пользователь задал вопрос: '{text}'. Ответь на вопрос."
        return ASK_QUESTIONS

# Обработка имени пользователя
async def ask_name(update: Update, context: CallbackContext):
    context.user_data['previous_state'] = ASK_QUESTIONS
    context.user_data['name'] = update.message.text
    question = "Спасибо. Какой у вас контактный номер?"
    await update.message.reply_text(question, reply_markup=back_button_markup())
    context.user_data['previous_question'] = question
    return ASK_CONTACT

# Обработка контактного номера
async def ask_contact(update: Update, context: CallbackContext):
    context.user_data['previous_state'] = ASK_NAME
    context.user_data['contact'] = update.message.text
    question = "Спасибо. В какой клинике вы хотите записаться?"
    await update.message.reply_text(question, reply_markup=back_button_markup())
    context.user_data['previous_question'] = question
    return ASK_CLINIC

# Обработка выбора клиники
async def ask_clinic(update: Update, context: CallbackContext):
    context.user_data['previous_state'] = ASK_CONTACT
    context.user_data['clinic'] = update.message.text
    question = "Спасибо. Какого врача вы предпочитаете?"
    await update.message.reply_text(question, reply_markup=back_button_markup())
    context.user_data['previous_question'] = question
    return ASK_DOCTOR

# Обработка выбора врача
async def ask_doctor(update: Update, context: CallbackContext):
    context.user_data['previous_state'] = ASK_CLINIC
    context.user_data['doctor'] = update.message.text
    question = "Спасибо. Когда вам удобно записаться на прием?"
    await update.message.reply_text(question, reply_markup=back_button_markup())
    context.user_data['previous_question'] = question
    return ASK_DATE

# Завершение диалога
async def ask_date(update: Update, context: CallbackContext):
    context.user_data['previous_state'] = ASK_DOCTOR
    context.user_data['date'] = update.message.text
    user_data = context.user_data
    summary = f"Имя: {user_data['name']}\nКонтакт: {user_data['contact']}\nКлиника: {user_data['clinic']}\нВрач: {user_data['doctor']}\нДата: {user_data['date']}"
    await update.message.reply_text(f"Ваши данные:\н{summary}\нСпасибо за запись!")
    return ConversationHandler.END

async def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

# Основной обработчик для запуска бота
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('new', start))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_QUESTIONS: [CallbackQueryHandler(ask_questions)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name), CallbackQueryHandler(back_handler)],
            ASK_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contact), CallbackQueryHandler(back_handler)],
            ASK_CLINIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_clinic), CallbackQueryHandler(back_handler)],
            ASK_DOCTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_doctor), CallbackQueryHandler(back_handler)],
            ASK_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date), CallbackQueryHandler(back_handler)]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    application.run_polling()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Определение стадий диалога
GREETING, OFFER, PREFERENCES, MENU, CHECK, FEEDBACK, BOOKING = range(7)

# Функция приветствия
def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text(
        f"Здравствуйте, {user.first_name}! Добро пожаловать в наш отельный бот. "
        "Я помогу вам с бронированием номера, начислением кэшбека и предоставлю лучшие предложения. "
        "Чем могу помочь сегодня?"
    )
    return GREETING

# Функция предложения бонуса
def offer(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "В честь вашего первого визита в наш бот, мы предлагаем вам бесплатный бокал шампанского или 100 бонусных баллов. "
        "Что бы вы предпочли?"
    )
    return OFFER

# Функция выявления предпочтений
def preferences(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Какой тип отдыха вы предпочитаете? У нас есть варианты для расслабляющего спа-отдыха, активных развлечений и деловых встреч."
    )
    return PREFERENCES

# Функция отображения меню
def menu(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Пожалуйста, ознакомьтесь с нашим каталогом предложений. Что вас интересует?"
    )
    return MENU

# Функция начисления кэшбека
def cashback(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Пожалуйста, введите сумму вашего чека для начисления кэшбека."
    )
    return CHECK

# Функция сбора отзывов
def feedback(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Как вам понравилось наше обслуживание? Пожалуйста, оставьте ваш отзыв."
    )
    return FEEDBACK

# Функция бронирования
def booking(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Хотели бы вы забронировать столик в ресторане или записаться на спа-процедуру? Пожалуйста, выберите удобное время."
    )
    return BOOKING

# Завершение диалога
def done(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Спасибо за использование нашего бота. Если у вас возникнут дополнительные вопросы, не стесняйтесь обращаться к нам."
    )
    return ConversationHandler.END

def main():
        application = ApplicationBuilder().token(TOKEN).build()

        application.add_handler(CommandHandler('new', start))
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                ASK_QUESTIONS: [CallbackQueryHandler(ask_questions)],
                ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name), CallbackQueryHandler(back_handler)],
                ASK_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contact), CallbackQueryHandler(back_handler)],
                ASK_CLINIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_clinic), CallbackQueryHandler(back_handler)],
                ASK_DOCTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_doctor), CallbackQueryHandler(back_handler)],
                ASK_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date), CallbackQueryHandler(back_handler)]
            },
            fallbacks=[]
        )

        application.add_handler(conv_handler)
        application.add_error_handler(error_handler)
        application.run_polling()


if __name__ == '__main__':
    main()

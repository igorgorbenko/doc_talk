import os
import json
import argparse
from datetime import datetime as dt
import asyncio
import logging
import httpx


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from telegram.constants import ChatAction

from openai_stuff.openai_stuff import OpenAIAssistant
from data_providers.google_sheets.google_sheets import GoogleSheetsClient


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
# Configure the httpx logger to only output warnings or higher level messages
logging.getLogger("httpx").setLevel(logging.WARNING)

FULL_NAME, PHONE_NUMBER, OTHER = range(3)

GOOGLE_SHEETS_CLIENT = GoogleSheetsClient(GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEET_URL)

from openai import OpenAI
OpenAI.api_key = OPENAI_API_KEY
client = OpenAI()


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Задать новый вопрос", callback_data='new_question')],
        [InlineKeyboardButton("Продолжить предыдущий диалог", callback_data='continue')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(GREETINGS_MESSAGE, reply_markup=reply_markup)


async def handle_message(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        'Прошу выбрать из представленных вариантов ниже',
        reply_markup=await start(update, context)
    )


async def handle_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'new_question':
        context.user_data['chat_id'] = query.message.chat_id
        context.user_data['thread'] = None
        await query.edit_message_text(text="Введите ваш вопрос:")
    elif query.data == 'continue':
        if 'thread' in context.user_data:
            await context.bot.send_message(chat_id=context.user_data['chat_id'],
                                           text="Продолжаем предыдущий диалог. Введите ваш вопрос:")
        else:
            await query.edit_message_text(text="Нет активных диалогов. Начните новый вопрос.")
    elif query.data == 'end_conversation':
        await query.edit_message_text(text="Спасибо за общение!")
        context.user_data.clear()


async def get_response(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    tg_username = update.effective_user.username
    context_thread_id = context.user_data.get('thread')

    # Проверяем, было ли последнее сообщение голосовым
    if 'transcript' in context.user_data:
        user_input = context.user_data['transcript']
        del context.user_data['transcript']
    else:
        user_input = update.message.text

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(1.2)

    try:
        logging.info(f'QUESTION: tg_username: {tg_username} - {user_input}')

        # Проверка, ожидается ли ввод ФИО или номера телефона
        if context.user_data.get('awaiting_full_name'):
            context.user_data['full_name'] = user_input
            context.user_data['awaiting_full_name'] = False
            # await update.message.reply_text('Спасибо, ваше ФИО сохранено.')
            # return

        if context.user_data.get('awaiting_phone_number'):
            context.user_data['phone_number'] = user_input
            context.user_data['awaiting_phone_number'] = False
            # await update.message.reply_text('Спасибо, ваш номер телефона сохранен.')
            # return

        if context_thread_id:
            response, _ = ASSISTANT_GPT.fetch_formatted_response(user_input=user_input, thread_id=context_thread_id)
        else:
            response, thread_id = ASSISTANT_GPT.fetch_formatted_response(user_input=user_input)
            context.user_data['thread'] = thread_id

        logging.info(f'ANSWER: tg_username: {tg_username} - {response}')

        if not context.user_data.get('full_name') and ("фио" in response.lower() or 'вас зовут' in response.lower()
                                                       or 'ваше полное имя' in response.lower()):
            # await update.message.reply_text("Пожалуйста, введите ваше полное имя (ФИО):")
            context.user_data['awaiting_full_name'] = True
            # return

        elif not context.user_data.get('phone_number') and ("контактный телефон" in response.lower()
                                                            or 'номер телефона' in response.lower()):
            # await update.message.reply_text("Пожалуйста, введите ваш номер телефона:")
            context.user_data['awaiting_phone_number'] = True
            # return
        elif "ДЕТАЛИ ЗАПИСИ:" in response:
            new_row = [dt.now().strftime('%d-%m-%Y'),
                       tg_username,
                       context.user_data['full_name'],
                       context.user_data['phone_number']]
            GOOGLE_SHEETS_CLIENT.append_row(new_row)
            context.user_data.clear()

        await context.bot.send_message(chat_id, text=response)

    except Exception as e:
        await context.bot.send_message(chat_id, text="Произошла ошибка: " + str(e))


async def handle_voice_message(update: Update, context: CallbackContext):
    logging.info('handle_voice_message called')
    voice_file = await update.message.voice.get_file()
    file_path = f'voice_{update.message.message_id}.ogg'
    await voice_file.download_to_drive(file_path)
    await update.message.reply_text("Голосовое сообщение получено, обрабатывается...")

    try:
        transcript = await transcribe_audio_with_openai(file_path)
        logging.info(f'Transcribed text: {transcript}')
        context.user_data['transcript'] = transcript
        await get_response(update, context)
    finally:
        # Удаление файла после обработки
        if os.path.exists(file_path):
            os.remove(file_path)


async def transcribe_audio_with_openai(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                timeout=httpx.Timeout(10)
                # timeout=httpx.Timeout(15.0, read=5.0, write=10.0, connect=3.0)
            )
        return response.text
    except httpx.RequestError as e:
        logging.error(f"An error occurred while requesting: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logging.error(f"Error response {e.response.status_code} while requesting {e.request.url}")
        raise
    except Exception as e:
        logging.error(f"Error while the calling the transcribe_audio_with_openai {str(e)}")
        raise


async def ask_for_full_name(update: Update, context: CallbackContext):
    logging.info(f'ask_for_full_name')
    # await update.message.reply_text("Please enter your full name (ФИО):", reply_markup=ForceReply(selective=True))
    return FULL_NAME


async def ask_for_phone_number(update: Update, context: CallbackContext):
    logging.info(f'ask_for_phone_number')
    context.user_data['full_name'] = update.message.text
    # await update.message.reply_text("Please enter your phone number:", reply_markup=ForceReply(selective=True))
    return PHONE_NUMBER


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text('Registration canceled.')
    return ConversationHandler.END


async def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    # # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_query))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_response))
    #
    # conv_handler = ConversationHandler(
    #     entry_points=[CallbackQueryHandler(handle_query)],
    #     states={
    #         FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_full_name)],
    #         PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_phone_number)],
    #         OTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_response)]
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )
    # Добавление обработчика ошибок
    application.add_error_handler(error_handler)

    # application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
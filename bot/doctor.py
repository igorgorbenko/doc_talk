import os
from datetime import datetime as dt
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from telegram.constants import ChatAction

from credentials import TOKEN
from openai_stuff.openai_stuff import OpenAIAssistant
from data_providers.google_sheets.google_sheets import GoogleSheetsClient


TOKEN = TOKEN

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

ASSISTANT_ID = "asst_84zHfX8FkiPGZaxX2BfAd2cm"
ASSISTANT_GPT = OpenAIAssistant(OPENAI_API_KEY, ASSISTANT_ID)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Configure the httpx logger to only output warnings or higher level messages
logging.getLogger("httpx").setLevel(logging.WARNING)

FULL_NAME, PHONE_NUMBER, OTHER = range(3)

GOOGLE_CREDENTIALS_PATH = '/Users/igor/__my_dev/doc_talk/bot/data_providers/google_sheets/sa-secret.json'
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1hqFgHAQ2nN6z2cBhrgv8HcXzcGdRA7O3ajkv-JTOJOo/edit#gid=0'
GOOGLE_SHEETS_CLIENT = GoogleSheetsClient(GOOGLE_CREDENTIALS_PATH, SPREADSHEET_URL)


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Задать новый вопрос", callback_data='new_question')],
        [InlineKeyboardButton("Продолжить предыдущий диалог", callback_data='continue')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Здравствуйте! 😊 Вас приветствует виртуальный ассистент стоматологической клиники. '
        '🦷 Я готов помочь вам с любыми вопросами! '
        'Вы можете узнать информацию о наших услугах, выбрать клинику, записаться на прием к врачу и многое другое. '
        'пше Задавайте любой вопрос! 💬',
        reply_markup=reply_markup
    )


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
    user_input = update.message.text
    chat_id = update.message.chat_id
    tg_username = update.effective_user.username
    context_thread_id = context.user_data.get('thread')

    print(context.user_data)

    # Send "typing..." action to show the bot is preparing a response
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # Simulate some processing time (if needed)
    await asyncio.sleep(1)  # Sleep for 1 second to mimic response time

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


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    # # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_query))
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

    # application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
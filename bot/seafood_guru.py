import os
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ChatAction

from credentials import TOKEN_SEAFOOD_GURU
from openai_stuff.openai_stuff import OpenAIAssistant


TOKEN = TOKEN_SEAFOOD_GURU

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

ASSISTANT_ID = "asst_Ti4C9k9Dw2Se3j9zxjqWGAoY"
ASSISTANT_GPT = OpenAIAssistant(OPENAI_API_KEY, ASSISTANT_ID)
USER_THREADS = {}


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Configure the httpx logger to only output warnings or higher level messages
logging.getLogger("httpx").setLevel(logging.WARNING)


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Задать новый вопрос", callback_data='new_question')],
        [InlineKeyboardButton("Продолжить предыдущий диалог", callback_data='continue')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Вас приветствует виртуальный ассистент по выбору морепродуктов. Задавайте любой вопрос!',
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

    # Send "typing..." action to show the bot is preparing a response
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # Simulate some processing time (if needed)
    await asyncio.sleep(1)  # Sleep for 1 second to mimic response time

    # message = await context.bot.send_message(chat_id, text="Готовлю для вас ответ...")
    try:
        logging.info(f'QUESTION: tg_username: {tg_username} - {user_input}')

        if context_thread_id:
            response, _ = ASSISTANT_GPT.fetch_formatted_response(user_input=user_input, thread_id=context_thread_id)
        else:
            response, thread_id = ASSISTANT_GPT.fetch_formatted_response(user_input=user_input)
            context.user_data['thread'] = thread_id

        logging.info(f'ANSWER: tg_username: {tg_username} - {response}')

        # await context.bot.delete_message(chat_id, message.message_id)
        # keyboard = [[InlineKeyboardButton("Завершить беседу", callback_data='end_conversation')]]
        # reply_markup = InlineKeyboardMarkup(keyboard)
        # Determine if this is potentially the last message in a conversation
        # For example, check if the response suggests concluding the interaction
        if "завершить" in response.lower():  # Assuming the response contains a hint to end the conversation
            keyboard = [[InlineKeyboardButton("Завершить беседу", callback_data='end_conversation')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = None

        # await context.bot.send_message(chat_id, text=response.choices[0].message.content, reply_markup=reply_markup)
        await context.bot.send_message(chat_id, text=response, reply_markup=reply_markup)
    except Exception as e:
        await context.bot.send_message(chat_id, text="Произошла ошибка: " + str(e))


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_response))

    application.run_polling()


if __name__ == '__main__':
    main()
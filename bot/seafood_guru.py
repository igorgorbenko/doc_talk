import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
# import openai

from credentials import TOKEN_SEAFOOD_GURU
from openai_stuff.openai_stuff import OpenAIAssistant


TOKEN = TOKEN_SEAFOOD_GURU
# openai.api_key = os.environ['OPENAI_API_KEY']

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
ASSISTANT_ID = "asst_Ti4C9k9Dw2Se3j9zxjqWGAoY"
ASSISTANT_GPT = OpenAIAssistant(OPENAI_API_KEY, ASSISTANT_ID)


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


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
    message = await context.bot.send_message(chat_id, text="Готовлю для вас ответ...")
    try:
        # response = openai.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "system", "content": "Ты - ассистент по выбору морепродуктов. Отвечай только на вопросы о рыбе и морепродуктах"},
        #               {"role": "user", "content": user_input}]
        # )
        response = ASSISTANT_GPT.fetch_formatted_response(user_input)

        await context.bot.delete_message(chat_id, message.message_id)
        keyboard = [[InlineKeyboardButton("Завершить беседу", callback_data='end_conversation')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # await context.bot.send_message(chat_id, text=response.choices[0].message.content, reply_markup=reply_markup)
        await context.bot.send_message(chat_id, text=response, reply_markup=reply_markup)
    except Exception as e:
        await context.bot.send_message(chat_id, text="Произошла ошибка: " + str(e))

# async def get_response(update: Update, context: CallbackContext) -> None:
#     user_input = update.message.text
#     chat_id = update.message.chat_id
#     message = await context.bot.send_message(chat_id, text="Готовлю для вас ответ...")
#
#     try:
#         # Check if a thread already exists; otherwise, create a new one
#         if 'thread_id' not in context.user_data:
#             # Create a new thread for the conversation
#             thread = openai.beta.threads.create()
#             context.user_data['thread_id'] = thread.id
#
#         # Send the message to the assistant within the thread
#         response = openai.beta.threads.messages.create(
#             thread_id=context.user_data['thread_id'],
#             role="user",
#             content="user_input"
#             model="gpt-3.5-turbo",
#             messages=[{"role": "system", "content": "Ты - ассистент по выбору морепродуктов. Отвечай только на вопросы о рыбе и морепродуктах"},
#                       {"role": "user", "content": user_input}]
#         )
#
#         # Delete the "Preparing response..." message
#         await context.bot.delete_message(chat_id, message.message_id)
#
#         # Setup the keyboard to allow ending the conversation
#         keyboard = [[InlineKeyboardButton("Завершить беседу", callback_data='end_conversation')]]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#
#         # Extracting the assistant's last message from the response
#         last_message = response['data'][-1]['content']
#
#         # Send the assistant's reply
#         await context.bot.send_message(chat_id, text=last_message, reply_markup=reply_markup)
#     except Exception as e:
#         # Handle exceptions, e.g., API errors, by sending an error message to the user
#         await context.bot.send_message(chat_id, text=f"Произошла ошибка: {str(e)}")



def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_response))

    application.run_polling()


if __name__ == '__main__':
    main()
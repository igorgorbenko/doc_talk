import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters, CallbackContext
from telegram.constants import ChatAction

import re

from credentials import TOKEN

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Configure the httpx logger to only output warnings or higher level messages
logging.getLogger("httpx").setLevel(logging.WARNING)


# Определяем состояния разговора
(NAME, PHONE, PROCEDURE, DOCTOR, DATE, TIME, CONFIRMATION) = range(7)


async def start(update: Update, context: CallbackContext, from_back=False):
    # Если функция вызвана через /cancel, update.message может быть None
    if update.message:
        chat_id = update.message.chat_id
        command = update.message.text
        if command == '/cancel':
            # Если вызов произошел через команду /cancel, отправляем сообщение о сбросе
            await update.message.reply_text('Диалог был сброшен. Давайте начнем заново!')
            await asyncio.sleep(0.5)  # Задержка перед следующим сообщением
        else:
            # Приветствие при стандартном вызове команды /start
            await update.message.reply_text('Привет! Я бот для записи в стоматологическую клинику')
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(0.5)  # Задержка для имитации печати
    else:
        # Если вызов произошел из callback_query (например, при возврате назад)
        chat_id = update.callback_query.message.chat_id
        await update.callback_query.answer()  # Ответ на callback_query
        await update.callback_query.edit_message_text('Давайте начнем заново! Пожалуйста, введите ваше имя:')

    # Отправка сообщения с запросом ввода имени
    message = "Пожалуйста, введите ваше имя:"
    await context.bot.send_message(chat_id=chat_id, text=message)
    return NAME


async def name(update: Update, context: CallbackContext, from_back=False):
    keyboard = [[InlineKeyboardButton("Вернуться назад", callback_data='return_to_start')]]

    message = "Пожалуйста, введите ваш контактный номер телефона:"
    if from_back:
        await update.callback_query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        chat_id = update.message.chat_id
        context.user_data['name'] = update.message.text
        logging.info(f"Сработала функция name. Пользователь ввел {context.user_data['name']}")

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(0.5)

        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    return PHONE


async def phone(update: Update, context: CallbackContext, from_back=False):
    keyboard = [
        [InlineKeyboardButton("Терапевт", callback_data='Терапевт'),
         InlineKeyboardButton("Хирург", callback_data='Хирург')],
        [InlineKeyboardButton("Имплантолог", callback_data='Имплантолог'),
         InlineKeyboardButton("Парадонтолог", callback_data='Парадонтолог')],
        [InlineKeyboardButton("Профчистка", callback_data='Профчистка')],
        [InlineKeyboardButton("Вернуться назад", callback_data='return_phone')]
    ]

    message = "Выберите направление:"
    if from_back:
        await update.callback_query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        phone_number = update.message.text

        if not re.match(r"^((8|\+7)[\-]?)?(\(?\d{3}\)?[\-]?)?[\d\-]{7,10}$", phone_number):
            await update.message.reply_text("Некорректный номер, попробуйте еще раз:")
            return PHONE
        context.user_data['phone'] = phone_number

        logging.info(f"Сработала функция phone. Пользователь ввел {phone_number}")

        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    return PROCEDURE


async def procedure(update: Update, context: CallbackContext, from_back=False):
    query = update.callback_query
    await query.answer()
    context.user_data['procedure'] = query.data
    logging.info(f"Сработала функция phone. Пользователь ввел {context.user_data['name']}")
    keyboard = [
        [InlineKeyboardButton("Доктор Игорь", callback_data='Доктор Игорь')],
        [InlineKeyboardButton("Доктор Яков", callback_data='Доктор Яков')],
        [InlineKeyboardButton("Вернуться назад", callback_data='return_procedure')]
    ]
    message = "Выберите доктора:"

    logging.info(f"Сработала функция procedure. Пользователь ввел {context.user_data['procedure'] }")

    if from_back:
        await update.callback_query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))
    return DOCTOR


async def doctor(update: Update, context: CallbackContext, from_back=False):
    query = update.callback_query
    await query.answer()
    context.user_data['doctor'] = query.data
    keyboard = [
        [InlineKeyboardButton("10.05.2024", callback_data='10.05.2024'),
         InlineKeyboardButton("12.05.2024", callback_data='12.05.2024')],
        [InlineKeyboardButton("Вернуться назад", callback_data='return_doctor')]
    ]
    message = "Выберите дату приема:"

    logging.info(f"Сработала функция doctor. Пользователь ввел {context.user_data['doctor']}")

    if from_back:
        await update.callback_query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))
    return DATE


async def date(update: Update, context: CallbackContext, from_back=False):
    query = update.callback_query
    await query.answer()
    context.user_data['date'] = query.data
    keyboard = [
        [InlineKeyboardButton("10:00", callback_data='10:00'),
         InlineKeyboardButton("11:00", callback_data='11:00')],
        [InlineKeyboardButton("Вернуться назад", callback_data='return_date')]
    ]
    message = "Выберите время приема:"

    logging.info(f"Сработала функция date. Пользователь ввел {context.user_data['date']}")

    if from_back:
        await update.callback_query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))
    return TIME


async def time(update: Update, context: CallbackContext, from_back=False):
    query = update.callback_query
    await query.answer()
    context.user_data['time'] = query.data

    user_name = context.user_data['name']
    user_phone = context.user_data['phone']
    procedure = context.user_data['procedure']
    doctor = context.user_data['doctor']
    date = context.user_data['date']
    time = context.user_data['time']

    keyboard = [
        [InlineKeyboardButton("Подтвердить запись", callback_data='confirm')],
        [InlineKeyboardButton("Вернуться назад", callback_data='return_time')]
    ]
    message = f"Уважаемый {user_name}, Вы будете записаны к {doctor}({procedure}) на {date} в {time}"

    logging.info(f"Сработала функция time. Пользователь ввел {context.user_data['time']}")

    if from_back:
        await update.callback_query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRMATION


async def back_to_previous(update: Update, context: CallbackContext):
    print('Invoked: back_to_previous')
    query = update.callback_query
    await query.answer()
    data = query.data

    logging.info(f"Received callback data: {data}")  # Логируем полученные данные

    handlers = {
        'return_to_start': (start, NAME),
        'return_phone': (name, PHONE),
        'return_procedure': (phone, PROCEDURE),
        'return_doctor': (doctor, DOCTOR),
        'return_date': (date, DATE),
        'return_time': (time, TIME)
    }

    if data in handlers:
        handler_function, state = handlers[data]
        logging.info(f"Calling handler {handler_function.__name__} with state {state}")
        return await handler_function(update, context, from_back=True)

    logging.error(f"No handler found for data: {data}")
    return ConversationHandler.END


def main():
    application = Application.builder().token(TOKEN).build()
    # application.add_handler(CommandHandler(['start', 'menu'], start))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(['start', 'menu'], start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE: [
                CallbackQueryHandler(back_to_previous, pattern='^return_'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, phone)
            ],
            PROCEDURE: [
                CallbackQueryHandler(back_to_previous, pattern='^return_'),
                CallbackQueryHandler(procedure)
            ],
            DOCTOR: [
                CallbackQueryHandler(back_to_previous, pattern='^return_'),
                CallbackQueryHandler(doctor),
            ],  # Add appropriate handlers
            DATE: [
                CallbackQueryHandler(back_to_previous, pattern='^return_'),
                CallbackQueryHandler(date),
            ],  # Add appropriate handlers
            TIME: [
                CallbackQueryHandler(back_to_previous, pattern='^return_'),
                CallbackQueryHandler(time),
            ],  # Add appropriate handlers
            CONFIRMATION: []  # Add appropriate handlers
        },
        fallbacks=[CommandHandler('cancel', start)],  # Option for canceling or restarting the dialog
        # per_message=True  # Устанавливаем per_message в True
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

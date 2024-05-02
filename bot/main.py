import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler)

from credentials import TOKEN

# Определение стадий диалога
# BRANCH, DOCTOR, PERSONAL_INFO, SCHEDULE, DATE = range(5)
BRANCH, PERSONAL_INFO, CONTACT_INFO, DOCTOR, SCHEDULE = range(5)
# PERSONAL_INFO, CONTACT = range(2)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Отключение логирования httpx
logging.getLogger('httpx').setLevel(logging.WARNING)


async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Новая запись", callback_data='new,')],
        [InlineKeyboardButton("Посмотреть мои записи", callback_data='view,')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f'Здравствуйте, {update.effective_user.first_name}! Я бот для записи на прием к врачу. '
        f'Вы можете выбрать одну из следующих команд:',
        reply_markup=reply_markup
    )


async def contact_handler(update: Update, context: CallbackContext):
    contact_keyboard = KeyboardButton(text="Отправить номер телефона", request_contact=True)
    custom_keyboard = [[contact_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keyboard=True)

    if update.callback_query:
        await update.callback_query.answer()  # Асинхронно ответить на callback_query
        await update.callback_query.message.reply_text('Пожалуйста, поделись своим номером телефона.', reply_markup=reply_markup)
    else:
        await update.message.reply_text('Пожалуйста, поделись своим номером телефона.', reply_markup=reply_markup)


async def help(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("<-- Назад", callback_data='view')],
        [InlineKeyboardButton("v Да", callback_data='view')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f'Мы постараемся помочь Вам как можно скорее, пожалуйста, напишите ниже свой вопрос',
        reply_markup=reply_markup
    )


async def new(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Branch 1", callback_data='select_branch,branch_1'),
         InlineKeyboardButton("Branch 2", callback_data='select_branch,branch_2')],
        [InlineKeyboardButton("Branch 3", callback_data='select_branch,branch_3'),
         InlineKeyboardButton("Branch 4", callback_data='select_branch,branch_4')],
        [InlineKeyboardButton("Branch 5", callback_data='select_branch,branch_5'),
         InlineKeyboardButton("Branch 6", callback_data='select_branch,branch_6')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    await query.message.reply_text('В каком филиале вы хотите записаться?', reply_markup=reply_markup)
    return BRANCH


async def view_appointments(update: Update, context: CallbackContext):
    await update.message.reply_text('Вот список ваших предстоящих записей:')
    # Добавьте код для вывода информации о записях пользователя


async def branch(update: Update, context: CallbackContext):
    branch = update.message.text
    context.user_data['branch'] = branch
    await update.message.reply_text('Пожалуйста, укажите ваше ФИО и контактные данные.')
    return PERSONAL_INFO


async def doctor(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Доктор Игорь", callback_data='doc_select,doctor_a'),
         InlineKeyboardButton("Доктор Яков", callback_data='doc_select,doctor_b')],
        [InlineKeyboardButton("Доктор Ринат", callback_data='doc_select,doctor_c')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text='Выберите врача:', reply_markup=reply_markup)
    return DOCTOR


async def personal_info(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    # Вы можете здесь запросить ФИО пациента, если это необходимо.
    await query.message.reply_text('Введите ФИО пациента')
    return PERSONAL_INFO


async def request_contact(update: Update, context: CallbackContext):
    context.user_data['full_name'] = update.message.text  # Сохраняем введенное ФИО
    await update.message.reply_text('Введите ваш контактный номер')
    return CONTACT_INFO


async def schedule(update: Update, context: CallbackContext):
    date = update.message.text
    context.user_data['date'] = date
    doctor = context.user_data['doctor']
    await update.message.reply_text(f'Вы записаны на {date} к доктору {doctor}. Спасибо!')
    return ConversationHandler.END


async def handle_unknown(update: Update, context: CallbackContext):
    await update.message.reply_text('Текст не распознан. Пожалуйста, выберите действие из меню ниже.')
    await start(update, context)  # Повторно вызываем функцию start для показа кнопок.


async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Очень важно вызвать этот метод для обработки нажатия на кнопку
    data = query.data  # 'callback_data' от кнопки
    action, value = data.split(',')

    if action == 'new':
        logging.info('New')
        # await new(update, context)
        await contact_handler(update, context)
    elif action == 'select_branch':
        logging.info('Branch selected')
        await doctor(update, context)
    elif action == 'doc_select':
        logging.info('Doc selected')
        await personal_info(update, context)
    elif action == 'view':
        await view_appointments(update, context)

    # Добавьте дополнительные условия для других кнопок по необходимости


def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CallbackQueryHandler(button_handler))  # Обработчик нажатий на кнопки

    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('personal_info', personal_info)],
        states={
            # BRANCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, branch)],
            PERSONAL_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal_info)],
            CONTACT_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_contact)],
            # DOCTOR: [MessageHandler( filters.TEXT & ~filters.COMMAND, doctor)],
            # SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule)],
        },
        fallbacks=[CommandHandler('start', start)]
    ))
    application.run_polling()


if __name__ == '__main__':
    main()



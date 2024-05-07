import logging
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

from credentials import TOKEN

# Определение стадий диалога
# NAME, PHONE, BRANCH, DOCTOR, SCHEDULE, CONTACT_INFO, PERSONAL_INFO = range(7)
BRANCH, DOCTOR, SCHEDULE, CONTACT_INFO, PERSONAL_INFO = range(5)


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Configure the httpx logger to only output warnings or higher level messages
logging.getLogger("httpx").setLevel(logging.WARNING)


async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Создать новую запись", callback_data='new')],
        [InlineKeyboardButton("Посмотреть мои записи", callback_data='view')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f'Здравствуйте, {update.effective_user.first_name}! Я бот для записи на прием к врачу. '
        f'Выберите одну из следующих опций:', reply_markup=reply_markup)

async def new(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Зорге 20", callback_data='branch_1'),
         InlineKeyboardButton("Копылова 14", callback_data='branch_2')],
        [InlineKeyboardButton("Павлюхина 25", callback_data='branch_3'),
         InlineKeyboardButton("Адоратского 148", callback_data='branch_4')],
        [InlineKeyboardButton("<-- Вернуться назад", callback_data='return_to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text('Выберите филиал:', reply_markup=reply_markup)
    return BRANCH

async def select_branch(update: Update, context: CallbackContext):
    branch = update.callback_query.data
    context.user_data['branch'] = branch
    keyboard = [
        [InlineKeyboardButton("Доктор Игорь", callback_data='doctor_a'),
         InlineKeyboardButton("Доктор Яша", callback_data='doctor_b')],
        [InlineKeyboardButton("Доктор Степан", callback_data='doctor_с'),
         InlineKeyboardButton("Доктор Иван", callback_data='doctor_в')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text('Выберите доктора:', reply_markup=reply_markup)
    return DOCTOR

async def select_doctor(update: Update, context: CallbackContext):
    doctor = update.callback_query.data
    context.user_data['doctor'] = doctor
    # Предложите пользователю выбрать время, предварительно загрузив доступные слоты
    # Для упрощения здесь используются захардкоженные времена
    keyboard = [
        [InlineKeyboardButton("10:00", callback_data='10:00'),
        InlineKeyboardButton("11:00", callback_data='11:00')],
        [InlineKeyboardButton("11:00", callback_data='12:00'),
        InlineKeyboardButton("11:00", callback_data='13:00')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text('Выберите время приема:', reply_markup=reply_markup)
    return SCHEDULE

async def select_time(update: Update, context: CallbackContext):
    time = update.callback_query.data
    context.user_data['time'] = time
    contact_keyboard = KeyboardButton("Отправить номер телефона", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_keyboard]], resize_keyboard=True, one_time_keyboard=True)
    await update.callback_query.message.reply_text('Пожалуйста, поделитесь вашим номером телефона для завершения записи.',
                                                   reply_markup=reply_markup)
    return CONTACT_INFO

# async def user_name(update: Update, context: CallbackContext):
#     user_name = update.message.text
#     context.user_data['user_name'] = user_name.lower()
#     # Здесь код для сохранения записи в базу данных и в Google Календарь
#     remove_keyboard = ReplyKeyboardRemove()  # Импортируйте ReplyKeyboardRemove из telegram
#     await update.message.reply_text(
#         f'Дорогой {user_name} просим Вас продолжить заполнение',
#         reply_markup=remove_keyboard
#     )
#     return NAME
#
# async def user_phone(update: Update, context: CallbackContext):
#     user_phone = update.message.text
#     context.user_data['user_phone'] = user_phone.lower()
#     # Здесь код для сохранения записи в базу данных и в Google Календарь
#     remove_keyboard = ReplyKeyboardRemove()  # Импортируйте ReplyKeyboardRemove из telegram
#     await update.message.reply_text(
#         f'Дорогой {context.user_data["user_name"]} с номером телефона {user_phone} просим Вас продолжить заполнение',
#         reply_markup=remove_keyboard
#     )
#     return PHONE

async def contact_info(update: Update, context: CallbackContext):
    contact = update.message.contact
    context.user_data['phone_number'] = contact.phone_number
    # Здесь код для сохранения записи в базу данных и в Google Календарь
    remove_keyboard = ReplyKeyboardRemove()  # Импортируйте ReplyKeyboardRemove из telegram
    await update.message.reply_text(
        f"Спасибо, ваша запись на {context.user_data['time']} к {context.user_data['doctor']} "
        f"в филиале {context.user_data['branch']} зарегистрирована.",
        reply_markup=remove_keyboard
    )
    return ConversationHandler.END

async def view_appointments(update: Update, context: CallbackContext):
    # Добавьте код для вывода информации о записях пользователя
    await update.callback_query.message.edit_text('Вот список ваших предстоящих записей:')

def setup_handlers(application):
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', start))
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(new, pattern='^new$'),
                      CallbackQueryHandler(view_appointments, pattern='^view$')],
        states={
            # NAME: [MessageHandler(filters.TEXT, callback=user_name)],
            # PHONE: [MessageHandler(filters.TEXT, callback=user_phone)],
            BRANCH: [CallbackQueryHandler(select_branch, pattern='^branch_'),
                     CallbackQueryHandler(back_to_previous, pattern='^return_')
                     ],
            DOCTOR: [CallbackQueryHandler(select_doctor, pattern='^doctor_')],
            SCHEDULE: [CallbackQueryHandler(select_time)],
            CONTACT_INFO: [MessageHandler(filters.CONTACT, contact_info)]
        },
        fallbacks=[CommandHandler('start', start)],
        # per_message=True
    ))

async def back_to_previous(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith('return_'):
        if data == 'return_to_start':
            await start(update, context)
            # await query.message.reply_text('Привет! Я бот для записи в стоматологическую клинику.\nПожалуйста, введите ваше имя:')
            # return NAME

    #     if data == 'return_to_start':
    #         await query.message.reply_text('Привет! Я бот для записи в стоматологическую клинику.\nПожалуйста, введите ваше имя:')
    #         return NAME
    #     elif data == 'return_phone':
    #         await query.message.reply_text("Введите ваш контактный номер телефона снова:")
    #         return PHONE
    #     elif data == 'return_procedure':
    #         return await procedure(update, context)
    return ConversationHandler.END


def main():
    application = Application.builder().token(TOKEN).build()
    setup_handlers(application)
    application.run_polling()

if __name__ == '__main__':
    main()


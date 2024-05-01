# import logging
#
# from telegram import Update, ReplyKeyboardMarkup, MenuButtonCommands, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext
#
# from credentials import TOKEN
#
# # Определение стадий диалога
# BRANCH, PERSONAL_INFO, DOCTOR, SCHEDULE, DATE = range(5)
#
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
#
#
# # async def start(update: Update, context):
# #     keyboard = [
# #         [InlineKeyboardButton("Новая запись", callback_data='new_appointment')],
# #         [InlineKeyboardButton("Посмотреть мои записи", callback_data='view')]
# #     ]
# #
# #     telegram_user_first_name = update.effective_user.first_name
# #     reply_markup = InlineKeyboardMarkup(keyboard)
# #     await update.message.reply_text(
# #         f'Здравствуйте, {telegram_user_first_name}! Я бот для записи на прием к врачу. '
# #         f'Вы можете выбрать одну из следующих команд:',
# #         # reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, one_time_keyboard=True, resize_keyboard=True)
# #         reply_markup=reply_markup
# #     )
# async def start(update: Update, context: CallbackContext):
#     keyboard = [
#         [InlineKeyboardButton("Новая запись", callback_data='new')],
#         [InlineKeyboardButton("Посмотреть мои записи", callback_data='view')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text(
#         f'Здравствуйте, {update.effective_user.first_name}! Я бот для записи на прием к врачу. '
#         f'Вы можете выбрать одну из следующих команд:',
#         reply_markup=reply_markup
#     )
#
# async def set_menu_button(bot):
#     menu_button = MenuButtonCommands('Меню')
#     await bot.set_chat_menu_button(menu_button=menu_button)
#
#
# async def new(update: Update, context):
#     reply_keyboard = [['Branch 1', 'Branch 2', 'Branch 3']]
#     await update.message.reply_text(
#         'В каком филиале вы хотите записаться?',
#         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
#     )
#     return BRANCH
#
# async def view(update: Update, context):
#     await update.message.reply_text('Вот список ваших предстоящих записей:')
#     # Здесь код для извлечения и отображения записей пользователя
#
# async def branch(update: Update, context):
#     branch = update.message.text
#     context.user_data['branch'] = branch
#     await update.message.reply_text('Пожалуйста, укажите ваше ФИО и контактные данные.')
#     return PERSONAL_INFO
#
#
# async def personal_info(update: Update, context):
#     user_info = update.message.text
#     context.user_data['personal_info'] = user_info
#     reply_keyboard = [['Doctor A', 'Doctor B', 'Doctor C']]
#     await update.message.reply_text(
#         'Выберите врача:',
#         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
#     )
#     return DOCTOR
#
#
# async def doctor(update: Update, context):
#     doctor = update.message.text
#     context.user_data['doctor'] = doctor
#     await update.message.reply_text('Выберите дату и время:')
#     return SCHEDULE
#
#
# async def schedule(update: Update, context):
#     date = update.message.text
#     context.user_data['date'] = date
#
#     doctor = context.user_data['doctor']
#     await update.message.reply_text(f'Вы записаны на {date} к доктору {doctor}. Спасибо!')
#     return ConversationHandler.END
#
#
# def handle_response(text: str) -> str:
#     proccessed_text: str = text.lower()
#
#     if 'оператор' in text:
#         return 'Наш диалог будет отправлен оператору. Наши клиника свяжется с Вами. Спасибо за обращение'
#
#     return 'Не понял ваш запрос, пожалуйста, повторите'
#
#
# async def handle_unknown(update: Update, context: CallbackContext):
#     await update.message.reply_text('Текст не распознан. Пожалуйста, выберите действие из меню ниже.')
#     # await start(update, context)  # Повторно вызываем функцию start для показа кнопок.
#
#
# def main():
#     application = Application.builder().token(TOKEN).build()
#
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('start', start)],
#         states={
#             BRANCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, branch)],
#             PERSONAL_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal_info)],
#             DOCTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, doctor)],
#             SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule)],
#         },
#         fallbacks=[CommandHandler('start', start)]
#     )
#
#     # Обработка команд "Новая запись" и "Посмотреть мои записи"
#     application.add_handler(CommandHandler('menu', start))
#     application.add_handler(CommandHandler('help', start))
#     # application.add_handler(MessageHandler(filters.Regex('^Новая запись$'), new_appointment))
#     # application.add_handler(MessageHandler(filters.Regex('^Посмотреть мои записи$'), view_appointments))
#     # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))
#
#     application.add_handler(conv_handler)
#     application.run_polling()
#     # application.bot_data.dispatcher.run_async(set_menu_button, application.bot)
#
#
# if __name__ == '__main__':
#     main()

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler)

from credentials import TOKEN

# Определение стадий диалога
BRANCH, PERSONAL_INFO, DOCTOR, SCHEDULE, DATE = range(5)

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


async def help(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("<-- Назад", callback_data='view')],
        [InlineKeyboardButton("v Да", callback_data='view')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f'Мы постараемся почомь Вам как можно скорее, пожалуйста, напишите ниже свой вопрос',
        reply_markup=reply_markup
    )


async def new(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Branch 1", callback_data='branch_select,branch_1'),
         InlineKeyboardButton("Branch 2", callback_data='branch_select,branch_2')],
        [InlineKeyboardButton("Branch 3", callback_data='branch_select,branch_3'),
         InlineKeyboardButton("Branch 4", callback_data='branch_select,branch_4')],
        [InlineKeyboardButton("Branch 5", callback_data='branch_select,branch_5'),
         InlineKeyboardButton("Branch 6", callback_data='branch_select,branch_6')]
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


async def personal_info(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    # Использование query.message для получения доступа к тексту сообщения
    user_info = query.message.text
    context.user_data['personal_info'] = user_info
    keyboard = [
        [InlineKeyboardButton("Doctor A", callback_data='doctor_a')],
        [InlineKeyboardButton("Doctor B", callback_data='doctor_b')],
        [InlineKeyboardButton("Doctor C", callback_data='doctor_c')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text='Выберите врача:', reply_markup=reply_markup)
    return DOCTOR


async def doctor(update: Update, context: CallbackContext):
    doctor = update.message.text
    context.user_data['doctor'] = doctor
    await update.message.reply_text('Выберите дату и время:')
    return SCHEDULE


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
        await new(update, context)
    elif action == 'branch_select':
        logging.info('Branch selected')
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
    # application.add_handler(ConversationHandler(
    #     entry_points=[CommandHandler('start', start)],
    #     states={
    #         BRANCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, branch)],
    #         PERSONAL_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal_info)],
    #         DOCTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, doctor)],
    #         SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule)],
    #     },
    #     fallbacks=[CommandHandler('start', start)]
    # ))
    application.run_polling()


if __name__ == '__main__':
    main()


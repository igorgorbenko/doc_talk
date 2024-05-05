# import logging
# import requests
#
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
# from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
#
# from credentials import TOKEN
#
# # Определение стадий диалога
# # NAME, PHONE, BRANCH, DOCTOR, SCHEDULE, CONTACT_INFO, PERSONAL_INFO = range(7)
# BRANCH, DOCTOR, SCHEDULE, CONTACT_INFO, PERSONAL_INFO = range(5)
#
#
# # Настройка логирования
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#
# async def start(update: Update, context: CallbackContext):
#     keyboard = [
#         [InlineKeyboardButton("Создать новую запись", callback_data='new')],
#         [InlineKeyboardButton("Посмотреть мои записи", callback_data='view')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text(
#         f'Здравствуйте, {update.effective_user.first_name}! Я бот для записи на прием к врачу. '
#         f'Выберите одну из следующих опций:', reply_markup=reply_markup)
#
# async def new(update: Update, context: CallbackContext):
#     keyboard = [
#         [InlineKeyboardButton("Филиал 1", callback_data='branch_1')],
#         [InlineKeyboardButton("Филиал 2", callback_data='branch_2')],
#         [InlineKeyboardButton("Филиал 3", callback_data='branch_3')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.callback_query.message.edit_text('Выберите филиал:', reply_markup=reply_markup)
#     return BRANCH
#
# async def select_branch(update: Update, context: CallbackContext):
#     branch = update.callback_query.data
#     context.user_data['branch'] = branch
#     keyboard = [
#         [InlineKeyboardButton("Доктор Игорь", callback_data='doctor_a')],
#         [InlineKeyboardButton("Доктор Яша", callback_data='doctor_b')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.callback_query.message.edit_text('Выберите доктора:', reply_markup=reply_markup)
#     return DOCTOR
#
# async def select_doctor(update: Update, context: CallbackContext):
#     doctor = update.callback_query.data
#     context.user_data['doctor'] = doctor
#     # Предложите пользователю выбрать время, предварительно загрузив доступные слоты
#     # Для упрощения здесь используются захардкоженные времена
#     keyboard = [
#         [InlineKeyboardButton("10:00", callback_data='10:00'),
#         InlineKeyboardButton("11:00", callback_data='11:00')],
#         [InlineKeyboardButton("11:00", callback_data='12:00'),
#         InlineKeyboardButton("11:00", callback_data='13:00')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.callback_query.message.edit_text('Выберите время приема:', reply_markup=reply_markup)
#     return SCHEDULE
#
# async def select_time(update: Update, context: CallbackContext):
#     time = update.callback_query.data
#     context.user_data['time'] = time
#     contact_keyboard = KeyboardButton("Отправить номер телефона", request_contact=True)
#     reply_markup = ReplyKeyboardMarkup([[contact_keyboard]], resize_keyboard=True, one_time_keyboard=True)
#     await update.callback_query.message.reply_text('Пожалуйста, поделитесь вашим номером телефона для завершения записи.',
#                                                    reply_markup=reply_markup)
#     return CONTACT_INFO
#
# # async def user_name(update: Update, context: CallbackContext):
# #     user_name = update.message.text
# #     context.user_data['user_name'] = user_name.lower()
# #     # Здесь код для сохранения записи в базу данных и в Google Календарь
# #     remove_keyboard = ReplyKeyboardRemove()  # Импортируйте ReplyKeyboardRemove из telegram
# #     await update.message.reply_text(
# #         f'Дорогой {user_name} просим Вас продолжить заполнение',
# #         reply_markup=remove_keyboard
# #     )
# #     return NAME
# #
# # async def user_phone(update: Update, context: CallbackContext):
# #     user_phone = update.message.text
# #     context.user_data['user_phone'] = user_phone.lower()
# #     # Здесь код для сохранения записи в базу данных и в Google Календарь
# #     remove_keyboard = ReplyKeyboardRemove()  # Импортируйте ReplyKeyboardRemove из telegram
# #     await update.message.reply_text(
# #         f'Дорогой {context.user_data["user_name"]} с номером телефона {user_phone} просим Вас продолжить заполнение',
# #         reply_markup=remove_keyboard
# #     )
# #     return PHONE
#
# async def contact_info(update: Update, context: CallbackContext):
#     contact = update.message.contact
#     context.user_data['phone_number'] = contact.phone_number
#     # Здесь код для сохранения записи в базу данных и в Google Календарь
#     remove_keyboard = ReplyKeyboardRemove()  # Импортируйте ReplyKeyboardRemove из telegram
#     await update.message.reply_text(
#         f"Спасибо, ваша запись на {context.user_data['time']} к {context.user_data['doctor']} "
#         f"в филиале {context.user_data['branch']} зарегистрирована.",
#         reply_markup=remove_keyboard
#     )
#     return ConversationHandler.END
#
# async def view_appointments(update: Update, context: CallbackContext):
#     # Добавьте код для вывода информации о записях пользователя
#     await update.callback_query.message.edit_text('Вот список ваших предстоящих записей:')
#
# def setup_handlers(application):
#     application.add_handler(CommandHandler('start', start))
#     application.add_handler(CommandHandler('menu', start))
#     application.add_handler(ConversationHandler(
#         entry_points=[CallbackQueryHandler(new, pattern='^new$'), CallbackQueryHandler(view_appointments, pattern='^view$')],
#         states={
#             # NAME: [MessageHandler(filters.TEXT, callback=user_name)],
#             # PHONE: [MessageHandler(filters.TEXT, callback=user_phone)],
#             BRANCH: [CallbackQueryHandler(select_branch, pattern='^branch_')],
#             DOCTOR: [CallbackQueryHandler(select_doctor, pattern='^doctor_')],
#             SCHEDULE: [CallbackQueryHandler(select_time)],
#             CONTACT_INFO: [MessageHandler(filters.CONTACT, contact_info)]
#         },
#         fallbacks=[CommandHandler('start', start)]
#     ))
#
# def main():
#     application = Application.builder().token(TOKEN).build()
#     setup_handlers(application)
#     application.run_polling()
#
# if __name__ == '__main__':
#     main()

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import openai

# Замените 'YOUR_TOKEN' на ваш токен от Telegram бота
TOKEN = '6670137750:AAHrVyYM567Hf995jSSAzOyV_ZQEKIOWEdM'
# Замените 'YOUR_OPENAI_API_KEY' на ваш ключ к API OpenAI
OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY


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
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Ты - ассистент по выбору морепродуктов. Отвечай только на вопросы о рыбе и морепродуктах"},
                      {"role": "user", "content": user_input}]
        )

        await context.bot.delete_message(chat_id, message.message_id)
        keyboard = [[InlineKeyboardButton("Завершить беседу", callback_data='end_conversation')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id, text=response.choices[0].message.content, reply_markup=reply_markup)
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
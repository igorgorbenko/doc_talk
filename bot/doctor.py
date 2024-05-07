#
# from credentials import TOKEN
#
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters, CallbackContext
#
# import re
#
# # Определяем состояния разговора
# (NAME, PHONE, PROCEDURE, DOCTOR, DATE, TIME, CONFIRMATION) = range(7)
#
# async def start(update: Update, context: CallbackContext):
#     await update.message.reply_text('Привет! Я бот для записи в стоматологическую клинику.\nПожалуйста, введите ваше имя:')
#     return NAME
#
# async def name(update: Update, context: CallbackContext):
#     context.user_data['name'] = update.message.text
#     await update.message.reply_text("Пожалуйста, введите ваш контактный номер телефона:")
#     return PHONE
#
# async def phone(update: Update, context: CallbackContext):
#     phone_number = update.message.text
#     if not re.match(r"^((8|\+7)[\-]?)?(\(?\d{3}\)?[\-]?)?[\d\-]{7,10}$", phone_number):
#         await update.message.reply_text("Некорректный номер, попробуйте еще раз:")
#         return PHONE
#     context.user_data['phone'] = phone_number
#     keyboard = [
#         [InlineKeyboardButton("Осмотр стоматолога", callback_data='dentist')],
#         [InlineKeyboardButton("Прием хирурга", callback_data='surgeon')],
#         [InlineKeyboardButton("Осмотр имплантолога", callback_data='implantologist')],
#         [InlineKeyboardButton("Консультация парадонтолога", callback_data='periodontist')],
#         [InlineKeyboardButton("Профчистка", callback_data='cleaning')],
#         [InlineKeyboardButton("Вернуться назад", callback_data='return_phone')]
#     ]
#     await update.message.reply_text('Выберите процедуру:', reply_markup=InlineKeyboardMarkup(keyboard))
#     return PROCEDURE
#
# async def procedure(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     if query.data == 'return_phone':
#         await query.message.reply_text("Пожалуйста, введите ваш контактный номер телефона снова:")
#         return PHONE
#     context.user_data['procedure'] = query.data
#     await query.edit_message_text(text="Выберите доктора:")
#     return DOCTOR
#
# async def back_to_previous(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     data = query.data
#     if data.startswith('return_'):
#         if data == 'return_to_start':
#             await query.message.reply_text('Привет! Я бот для записи в стоматологическую клинику.\nПожалуйста, введите ваше имя:')
#             return NAME
#         elif data == 'return_phone':
#             await query.message.reply_text("Введите ваш контактный номер телефона снова:")
#             return PHONE
#         elif data == 'return_procedure':
#             return await procedure(update, context)
#     return ConversationHandler.END
#
# def main():
#     application = Application.builder().token(TOKEN).build()
#     application.add_handler(CommandHandler('start', start))
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('start', start)],
#         states={
#             NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
#             PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
#             PROCEDURE: [
#                 CallbackQueryHandler(procedure),
#                 CallbackQueryHandler(back_to_previous, pattern='^return_')
#             ],
#             DOCTOR: [],
#             DATE: [],
#             TIME: [],
#             CONFIRMATION: []
#         },
#         fallbacks=[CommandHandler('cancel', start)]
#     )
#     application.add_handler(conv_handler)
#     application.run_polling()
#
# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(main())
#
#
#
# #
# # from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# # from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters, CallbackContext
# #
# # import re
# #
# # # Определяем состояния разговора
# # (NAME, PHONE, PROCEDURE, DOCTOR, DATE, TIME, CONFIRMATION) = range(7)
# #
# # async def start(update: Update, context: CallbackContext):
# #     await update.message.reply_text('Привет! Я бот для записи в стоматологическую клинику.\nПожалуйста, введите ваше имя:')
# #     return NAME
# #
# # async def name(update: Update, context: CallbackContext):
# #     context.user_data['name'] = update.message.text
# #     await update.message.reply_text("Пожалуйста, введите ваш контактный номер телефона:")
# #     return PHONE
# #
# # async def phone(update: Update, context: CallbackContext):
# #     phone_number = update.message.text
# #     if not re.match(r"^((8|\+7)[\-]?)?(\(?\d{3}\)?[\-]?)?[\d\-]{7,10}$", phone_number):
# #         await update.message.reply_text("Некорректный номер, попробуйте еще раз:")
# #         return PHONE
# #     context.user_data['phone'] = phone_number
# #     keyboard = [
# #         [InlineKeyboardButton("Осмотр стоматолога", callback_data='dentist')],
# #         [InlineKeyboardButton("Прием хирурга", callback_data='surgeon')],
# #         [InlineKeyboardButton("Осмотр имплантолога", callback_data='implantologist')],
# #         [InlineKeyboardButton("Консультация парадонтолога", callback_data='periodontist')],
# #         [InlineKeyboardButton("Профчистка", callback_data='cleaning')]
# #     ]
# #     await update.message.reply_text('Выберите процедуру:', reply_markup=InlineKeyboardMarkup(keyboard))
# #     return PROCEDURE
# #
# # async def procedure(update: Update, context: CallbackContext):
# #     query = update.callback_query
# #     await query.answer()
# #     context.user_data['procedure'] = query.data
# #     await query.edit_message_text(text="Выберите доктора:")
# #     return DOCTOR
# #
# # def main():
# #     application = Application.builder().token(TOKEN).build()
# #     conv_handler = ConversationHandler(
# #         entry_points=[CommandHandler('start', start)],
# #         states={
# #             NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
# #             PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
# #             PROCEDURE: [CallbackQueryHandler(procedure)],
# #             DOCTOR: [CallbackQueryHandler(procedure)],  # Убедитесь, что ваши обработчики соответствуют логике
# #             DATE: [],
# #             TIME: [],
# #             CONFIRMATION: []
# #         },
# #         fallbacks=[CommandHandler('cancel', start)]
# #     )
# #     application.add_handler(conv_handler)
# #     application.run_polling()
# #
# # if __name__ == '__main__':
# #     import asyncio
# #     asyncio.run(main())

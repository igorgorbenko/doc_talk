import logging

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters, \
    ConversationHandler, CallbackQueryHandler
from telegram.constants import ChatAction
import requests


TOKEN = ""
BOT_USERNAME = "ai_assist_travel_vendor_bot"

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Определение состояний
CARD_NUMBER, AMOUNT, CONFIRM = range(3)


# Основное меню
async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user = update.message.from_user
    tg_user_params = {'tg_id': user.id}

    response = requests.post("http://127.0.0.1:8000/check_vendor_by_user", json=tg_user_params)
    if response.status_code == 200:
        user_type = response.json()['user_type']
        if user_type != 'Vendor':
            await update.message.reply_text(f'Вы не являетесь сотрудником одного из наши поставщиков')
            return

        kb = [
            [KeyboardButton("🍽️ Бронирования для подтверждения")],
            [KeyboardButton("💸 Начислить кэшбек")]
        ]
        reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)

        await update.message.reply_text('Привет! Я консьерж-бот для организации досуга')
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await update.message.reply_text("Пожалуйста, выберите один из вариантов на клавиатуре ниже:",
                                        reply_markup=reply_markup)


async def handle_cashback(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Введите номер участника программы (от 1000 до 9999):")
    return CARD_NUMBER


async def received_card_number(update: Update, context: CallbackContext) -> int:
    card_number = update.message.text
    if not card_number.isdigit() or not (1000 <= int(card_number) <= 9999):
        await update.message.reply_text(
            "Неверный номер участника программы. Пожалуйста, введите число от 1000 до 9999 или нажмите /cancel для отмены.")
        return CARD_NUMBER

    context.user_data['card_number'] = card_number
    await update.message.reply_text("Введите сумму чека:")
    return AMOUNT


async def received_amount(update: Update, context: CallbackContext) -> int:
    amount = update.message.text
    try:
        amount = float(amount)
        context.user_data['amount'] = amount

        card_number = context.user_data['card_number']
        message = f"Проверьте данные перед сохранением:\n\nНомер участника: {card_number}\nСумма чека: {amount}"

        keyboard = [
            [InlineKeyboardButton("Сохранить", callback_data='save')],
            [InlineKeyboardButton("Отменить", callback_data='cancel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, reply_markup=reply_markup)
        return CONFIRM
    except ValueError:
        await update.message.reply_text(
            "Неверная сумма. Пожалуйста, введите числовое значение или нажмите /cancel для отмены.")
        return AMOUNT


async def confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query_data = query.data

    if query_data == 'save':
        # Сохранение визита в базу данных
        # TODO: Реализуйте сохранение данных в базу данных
        await query.edit_message_text("Запись успешно сохранена!")
    elif query_data == 'cancel':
        await query.edit_message_text("Действие отменено.")

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END


async def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)


# Обработка нажатий на Inline кнопки для подтверждения или отклонения бронирования
async def handle_callback_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data = query.data

    if query_data.startswith("confirm_") or query_data.startswith("reject_"):
        status = 'Confirmed'
        if query_data.startswith("reject_"):
            status = 'Rejected'

        booking_id = query_data.split("_")[1]
        # TODO: Добавьте логику для подтверждения бронирования в базе данных
        response_booking_status = requests.post("http://127.0.0.1:8000/update_booking_status",
                                                json={"booking_id": booking_id,
                                                      "status": status})
        if response_booking_status.status_code == 200:
            response_notification = requests.post("http://127.0.0.1:8000/notify_customer",
                                                  json={"booking_id": booking_id})
            if response_notification.status_code == 200:
                await query.edit_message_text(f"Бронирование ID = {booking_id} обработано")
            else:
                logging.error(f"There is an error during the notify the customer Booking ID = {booking_id}, "
                              f"error: {response_notification.error}")
                await query.edit_message_text(f"При обработке бронирования ID = {booking_id} возникли проблемы")
        else:
            await query.edit_message_text(f"При обработке бронирования ID = {booking_id} возникли проблемы")
            logging.error(f"There is an error during the update Booking ID = {booking_id}, "
                          f"error: {response_booking_status.error}")

    # Логика для других обработчиков callback_data может быть добавлена здесь


if __name__ == '__main__':
    # Создание Telegram приложения
    application = ApplicationBuilder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler('start', start))

    # Conversation handler для начисления кэшбека
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('💸 Начислить кэшбек'), handle_cashback)],
        states={
            CARD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_card_number)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_amount)],
            CONFIRM: [CallbackQueryHandler(confirm)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler)

    # Обработчик нажатий на Inline кнопки
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Запуск бота
    logging.info(f"Your bot is listening! Navigate to http://t.me/{BOT_USERNAME} to interact with it!")
    application.run_polling()

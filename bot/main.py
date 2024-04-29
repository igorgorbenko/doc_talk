from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters

from credentials import TOKEN

# Определение стадий диалога
BRANCH, PERSONAL_INFO, DOCTOR, SCHEDULE, DATE = range(5)

async def start(update: Update, context):
    # Определение кнопок для выбора филиала
    reply_keyboard = [['Branch 1', 'Branch 2', 'Branch 3']]

    # Отправка сообщения с клавиатурой
    await update.message.reply_text(
        'Привет! В каком филиале вы хотите записаться?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return BRANCH

async def branch(update: Update, context):
    branch = update.message.text
    context.user_data['branch'] = branch
    # print('update.effective_user.name', update.effective_user.name)
    # print('update.effective_user.id', update.effective_user.id)
    await update.message.reply_text('Пожалуйста, укажите ваше ФИО и контактные данные.')
    return PERSONAL_INFO

async def personal_info(update: Update, context):
    user_info = update.message.text
    context.user_data['personal_info'] = user_info
    reply_keyboard = [['Doctor A', 'Doctor B', 'Doctor C']]
    await update.message.reply_text(
        'Выберите врача:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return DOCTOR

async def doctor(update: Update, context):
    doctor = update.message.text
    context.user_data['doctor'] = doctor
    await update.message.reply_text('Выберите дату и время:')
    return SCHEDULE

async def schedule(update: Update, context):
    date = update.message.text
    context.user_data['date'] = date
    await update.message.reply_text(f'Вы записаны на {date}. Спасибо!')
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BRANCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, branch)],
            PERSONAL_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal_info)],
            DOCTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, doctor)],
            SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()

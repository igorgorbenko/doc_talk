# from telegram import Update
# from telegram.ext import Application, CommandHandler, ContextTypes
#
# from credentials import TOKEN
#
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     user = update.effective_user
#     await update.message.reply_text(
#         f"Ваш Telegram ID: {user.id}\n"
#         f"Ваше имя пользователя: @{user.username}"
#     )
#
# def main() -> None:
#     application = Application.builder().token(TOKEN).build()
#     application.add_handler(CommandHandler("start", start))
#     application.run_polling()
#
# if __name__ == '__main__':
#     main()

# 433292846

import asyncio
from telegram import Update
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes

from credentials import TOKEN

async def send_message_to_user(bot_token, user_id, message_text):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=user_id, text=message_text)

# Функция для запуска асинхронного кода
async def main():
    bot_token = TOKEN
    user_id = 433292846  # Уникальный ID пользователя
    message_text = "Привет! Это автоматическое сообщение от вашего бота."
    await send_message_to_user(bot_token, user_id, message_text)

# Запуск асинхронного цикла событий
if __name__ == '__main__':
    asyncio.run(main())
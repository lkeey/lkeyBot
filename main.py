from dotenv import load_dotenv
import os

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram import (
    Update,
)

from db.database import create_db, register_user, get_all_users

import asyncio

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await register_user(
        user_id=user_id,
        username=update.effective_user.username,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы успещно зарегистрированы",
    )


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="hello",
    )

    users = await get_all_users()

    print(users)


async def fff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Получил ваше обращение",
    )


def main():
    print("MAIN")

    TOKEN = os.getenv("TOKEN")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("hello", hello))

    application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())

    main()

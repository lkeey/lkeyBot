from dotenv import load_dotenv
import os
import aiosqlite

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
from telegram import (
    Update,
)

from states import GET_QUESTION, GET_QUESTION_FOR_POLL

from db.database import create_db, register_user, get_all_users

import asyncio, json

DB_PATH = "users.db"

GROUP_ID = "-1002394139708"

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT username FROM users WHERE id_tg = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="С возвращением!",
                )
            else:
                await register_user(
                    user_id=user_id,
                    username=update.effective_user.username,
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Вы успещно зарегистрированы",
                )
    return 0


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="hello",
    )

    users = await get_all_users()

    print(users)


async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите ваш вопрос:",
    )
    return GET_QUESTION


async def save_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=update.message.text,
    )


async def create_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="Создание опроса!\n\nВведите вопрос",
    )

    return GET_QUESTION_FOR_POLL


async def create_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("polls.json", "r") as f:
        polls = json.load(f)

    polls[max(polls.keys()) + 1] = {"question": update.message.text}

    with open("polls.json", "w") as f:
        json.dump(polls, f)

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="Создание опроса!\n\nВведите опции",
    )

    print()

    return 0


def main():
    print("MAIN")

    TOKEN = os.getenv("TOKEN")

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_question)
            ],
            GET_QUESTION_FOR_POLL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_task)
            ],
        },
        fallbacks=[
            CommandHandler("question", get_question),
            CommandHandler("createpoll", create_poll),
        ],
        persistent=False,
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())

    main()

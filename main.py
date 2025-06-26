from dotenv import load_dotenv
import os
import aiosqlite

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup


from db.database import create_db, register_user

from static.text import (
    GREETING,
    ABOUT_INTENSIV,
    DESCRIPTION_1,
    DESCRIPTION_2,
    DELAYED_MESSAGE,
)

import asyncio

DB_PATH = "users.db"

GROUP_ID = "-1002394139708"

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🌐 Об интенсиве", callback_data="about_course")]]
    )

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT username FROM users WHERE id_tg = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                await register_user(
                    user_id=user_id,
                    username=update.effective_user.username,
                )

    with open("img/7M307113.JPG", "rb") as f:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=f,
            caption=GREETING,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


async def about_course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔹 Базовый курс", callback_data="basic_course")],
            [
                InlineKeyboardButton(
                    "🔸 Продвинутый курс", callback_data="advanced_course"
                )
            ],
        ]
    )

    with open("img/course_1.jpg", "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption=ABOUT_INTENSIV,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


async def intensiv_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔹 Базовый курс", callback_data="basic_course")],
            [
                InlineKeyboardButton(
                    "🔸 Продвинутый курс", callback_data="advanced_course"
                )
            ],
        ]
    )

    with open("img/course_1.jpg", "rb") as photo:
        await context.bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=ABOUT_INTENSIV,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


async def course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    bot = context.bot

    if query.data == "basic_course":
        with open("img/course_2.jpg", "rb") as photo:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📝 Записаться", url="https://t.me/m/boXhH69MYzRi"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⚡️ Подробнее", url="http://by.lkey.tilda.ws/base"
                        )
                    ],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="about_course")],
                ]
            )

            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=DESCRIPTION_1,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )

    elif query.data == "advanced_course":
        with open("img/course_3.jpeg", "rb") as photo:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📝 Записаться", url="https://t.me/m/jWlVlaBRMWZi"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⚡️ Подробнее", url="http://by.lkey.tilda.ws/super"
                        )
                    ],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="about_course")],
                ]
            )

            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=DESCRIPTION_2,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )

    asyncio.create_task(send_follow_up(chat_id, bot))


async def send_follow_up(chat_id, bot):
    await asyncio.sleep(30)

    with open("img/course_4.jpg", "rb") as photo:
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption="❓ Ещё не готов купить?\n\n🤩 Посмотри более подробную информацию на нашем сайте:\n\nhttp://by.lkey.tilda.ws/",
            parse_mode="Markdown",
        )


def main():
    print("MAIN")

    # TOKEN = os.getenv("TOKEN")
    TOKEN = "8025550158:AAEVGc6fHWZb6e1Xlh3DNXpYgfhoxi3jP48"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", intensiv_info))

    application.add_handler(
        CallbackQueryHandler(about_course_callback, pattern="about_course")
    )
    application.add_handler(
        CallbackQueryHandler(
            course_callback, pattern="^(basic_course|advanced_course)$"
        )
    )

    application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())

    main()

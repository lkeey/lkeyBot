from dotenv import load_dotenv
import os
import aiosqlite
from datetime import datetime

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup


from db.database import (
    create_db,
    register_user,
    calculate_conversion,
    update_status,
    export_to_excel,
)

from static.text import (
    GREETING,
    ABOUT_INTENSIV,
    DESCRIPTION_1,
    DESCRIPTION_2,
    PLEASE_SUBSCRIBE,
)

from static.states_list import states_list

from static.ids import CHANNEL_USERNAME, ADMINS

import asyncio

DB_PATH = "users.db"
EXCEL_PATH = "users_export.xlsx"

load_dotenv()


async def is_subscribed(user_id, context) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)

        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"error - {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🌐 Об интенсиве", callback_data="about_course")]]
    )

    channel = "нет информации"
    if len(context.args) > 0:
        channel = context.args[0]

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT username FROM users WHERE id_tg = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
                await register_user(
                    user_id=user_id,
                    username=update.effective_user.username,
                    channel=channel,
                    date=current_date,
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
    user_id = update.effective_user.id

    await query.answer()

    if await is_subscribed(user_id, context):
        await update_status(
            update.effective_user.id,
            2,  # подписался
        )

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
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Подписаться", url="https://t.me/+zO1-XmalT2xhNzMy"
                    )
                ],
            ]
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=PLEASE_SUBSCRIBE,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

        context.job_queue.run_once(
            send_is_subscribed,
            10,
            chat_id=update.effective_chat.id,
            name="CHECK_IF_SUBSCRIBED",
        )


async def intensiv_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    subc = await is_subscribed(user_id, context)

    if subc:
        await update_status(
            update.effective_user.id,
            2,  # подписался
        )

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
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Подписаться", url="https://t.me/+zO1-XmalT2xhNzMy"
                    )
                ],
            ]
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=PLEASE_SUBSCRIBE,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

        context.job_queue.run_once(
            send_is_subscribed,
            10,
            chat_id=update.effective_chat.id,
            name="CHECK_IF_SUBSCRIBED",
        )


async def course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await update_status(
        update.effective_user.id,
        3,  # открыл описание
    )

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

    # отправляем прогревочное сообщение
    context.job_queue.run_once(
        send_follow_up,
        900,  # 15 мин
        chat_id=update.effective_chat.id,
        name="SEND_PROGREV_MESSAGE",
    )


async def send_follow_up(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job

    with open("img/course_4.jpg", "rb") as photo:
        await context.bot.send_photo(
            chat_id=job.chat_id,
            photo=photo,
            caption="❓ Ещё не готов купить?\n\n🤩 Посмотри более подробную информацию на нашем сайте:\n\nhttp://by.lkey.tilda.ws/",
            parse_mode="Markdown",
        )


async def admin_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in ADMINS:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🌐 Конверсии", callback_data="get_conversions")]]
        )

        await context.bot.send_message(
            chat_id=user_id,
            text="Выберите команду",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text="Вы не админ :(",
        )


async def get_conversions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id

    number_users = await calculate_conversion()
    message = f"{states_list[1]}"
    for n, number in enumerate(number_users[1:]):
        if number_users[n] > 0:
            conversion = round(number_users[n + 1] / number_users[n] * 100, 2)
        else:
            conversion = 0
        message += f"\n|\n|    {conversion}%\nv\n{states_list[n + 2]}"

    total_conversion = round(number_users[-1] / number_users[0] * 100, 2)
    message += f"\n\nОбщая конверсия из зашедших в оплату — {total_conversion}%"

    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
    )


async def setstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        return

    if len(context.args) != 2:
        await update.message.reply_text(
            "Использование: /setstatus <tg_id> <new_status>"
        )
        return

    await update_status(
        context.args[0],
        int(context.args[1]),  # новый статус
    )

    await update.message.reply_text(
        f"Статус пользователя {context.args[0]} обновлён на {context.args[1]}."
    )


async def send_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        return

    try:
        await export_to_excel()
        with open(EXCEL_PATH, "rb") as file:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=file,
                filename=EXCEL_PATH,
                caption="📄 Конверсии",
            )
        os.remove(EXCEL_PATH)
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")


async def send_is_subscribed(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Подписаться", url="https://t.me/+zO1-XmalT2xhNzMy")],
            [InlineKeyboardButton("Конечно", callback_data="yes_subscribed")],
        ],
    )

    await context.bot.send_message(
        job.chat_id, text="🤩 Уже подписался?", reply_markup=keyboard
    )


async def send_retry_if_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()

    user_id = update.effective_user.id

    if await is_subscribed(user_id, context):
        await update_status(
            update.effective_user.id,
            2,  # подписался
        )

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
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Подписаться", url="https://t.me/+zO1-XmalT2xhNzMy"
                    )
                ],
                [InlineKeyboardButton("Конечно", callback_data="yes_subscribed")],
            ],
        )

        await context.bot.send_message(
            update.effective_chat.id,
            text="💥 Скорее подписывайся!",
            reply_markup=keyboard,
        )


def main():
    print("MAIN")

    TOKEN = os.getenv("TOKEN")

    # for test
    # TOKEN = "7942617995:AAGc7e6F2WsDL0EpsD8E5DroDK0q9hKwY-Q"

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", intensiv_info))
    application.add_handler(CommandHandler("admin", admin_commands))

    application.add_handler(
        CallbackQueryHandler(about_course_callback, pattern="about_course")
    )
    application.add_handler(
        CallbackQueryHandler(
            course_callback, pattern="^(basic_course|advanced_course)$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(get_conversions_callback, pattern="get_conversions")
    )
    application.add_handler(CommandHandler("setstatus", setstatus))

    application.add_handler(CommandHandler("excel", send_excel))

    application.add_handler(
        CallbackQueryHandler(send_retry_if_subscribed, pattern="yes_subscribed")
    )

    application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())

    main()

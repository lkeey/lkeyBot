import aiosqlite
import pandas as pd

DB_PATH = "users.db"
EXCEL_PATH = "users_export.xlsx"


async def create_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,    
                id_tg INTEGER DEFAULT 0,
                username TEXT,
                channel TEXT DEFAULT "нет данных",
                status INTEGER DEFAULT 1,
                date TEXT DEFAULT "нет данных"
            )
        """)
        await db.commit()


async def register_user(user_id, username, channel, date):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (id_tg, username, channel, date) 
            VALUES (?, ?, ?, ?)
            """,
            (user_id, username, channel, date),
        )
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            return users


async def calculate_conversion():
    db = await aiosqlite.connect(DB_PATH)
    total_users = await db.execute("""SELECT COUNT(*) FROM users WHERE status >= 1""")
    total_users = await total_users.fetchone()
    total_users = total_users[0]
    number_users = [total_users]
    list_statuses = [1, 2, 3, 4]
    for status in list_statuses:
        total_users_with_status = await db.execute(
            """SELECT COUNT(*) FROM users WHERE status >= ?""", (status,)
        )
        total_users_with_status = await total_users_with_status.fetchone()
        total_users_with_status = total_users_with_status[0]
        number_users.append(total_users_with_status)
    return number_users


async def update_status(id_tg, status):
    async with aiosqlite.connect(DB_PATH) as db:
        # Получаем текущий статус
        async with db.execute(
            "SELECT status FROM users WHERE id_tg = ?", (id_tg,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                # Если пользователя нет, можно вставить или просто вернуть
                print("Пользователь не найден")
                return

            current_status = row[0]
            if status > current_status:
                await db.execute(
                    "UPDATE users SET status = ? WHERE id_tg = ?", (status, id_tg)
                )
                await db.commit()


async def export_to_excel():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users")
        rows = await cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        await cursor.close()

    df = pd.DataFrame(rows, columns=columns)
    df.to_excel(EXCEL_PATH, index=False)

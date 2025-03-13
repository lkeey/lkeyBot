import aiosqlite

DB_PATH = "users.db"


async def create_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,    
                id_tg INTEGER DEFAULT 0,
                username TEXT,
                points INTEGER DEFAULT 0
            )
        """)
        await db.commit()


async def register_user(user_id, username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (id_tg, username) 
            VALUES (?, ?)
            """,
            (user_id, username),
        )
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            return users

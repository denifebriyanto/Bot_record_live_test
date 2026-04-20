import aiosqlite
import asyncio

DB_FILE = "data.db"

_db_lock = asyncio.Lock()


async def init_db():
    async with _db_lock:
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS watches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    username TEXT,
                    added_by INTEGER
                )
            """)
            await db.commit()


async def add_watch(chat_id, username, added_by):
    async with _db_lock:
        async with aiosqlite.connect(DB_FILE) as db:

            cur = await db.execute(
                "SELECT 1 FROM watches WHERE chat_id=? AND username=?",
                (chat_id, username)
            )

            exists = await cur.fetchone()

            if exists:
                return False

            await db.execute(
                "INSERT INTO watches (chat_id, username, added_by) VALUES (?, ?, ?)",
                (chat_id, username, added_by)
            )

            await db.commit()

            return True


async def remove_watch(chat_id, username):
    async with _db_lock:
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(
                "DELETE FROM watches WHERE chat_id=? AND username=?",
                (chat_id, username)
            )

            await db.commit()


async def get_watchlist(chat_id):
    async with _db_lock:
        async with aiosqlite.connect(DB_FILE) as db:

            cur = await db.execute(
                "SELECT username FROM watches WHERE chat_id=?",
                (chat_id,)
            )

            rows = await cur.fetchall()

            return [r[0] for r in rows]


async def get_all_watches():
    async with _db_lock:
        async with aiosqlite.connect(DB_FILE) as db:

            cur = await db.execute(
                "SELECT chat_id, username FROM watches"
            )

            rows = await cur.fetchall()

            return rows

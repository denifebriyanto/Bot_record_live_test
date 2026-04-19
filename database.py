import aiosqlite

DB_PATH = "watchlist.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            username TEXT,
            added_by INTEGER,
            UNIQUE(chat_id, username)
        )
        """)
        await db.commit()


async def add_watch(chat_id: int, username: str, added_by: int):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO watchlist (chat_id, username, added_by) VALUES (?, ?, ?)",
                (chat_id, username, added_by)
            )
            await db.commit()
            return True
        except:
            return False


async def remove_watch(chat_id: int, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM watchlist WHERE chat_id=? AND username=?",
            (chat_id, username)
        )
        await db.commit()


async def get_watchlist(chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT username FROM watchlist WHERE chat_id=?",
            (chat_id,)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def get_all_watches():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT chat_id, username FROM watchlist"
        )
        return await cursor.fetchall()

import aiosqlite

DB_PATH = "bdd.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS config (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER,
                autorole_id INTEGER
            )
        """)
        await db.commit()

async def get_log_channel(bot, guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT log_channel_id FROM config WHERE guild_id = ?",
            (guild_id,)
        )
        row = await cursor.fetchone()

    if row is None or row[0] is None:
        return None

    return bot.get_channel(row[0])

async def add_warn(guild_id, user_id, moderator_id, reason):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO warns (guild_id, user_id, moderator_id, reason) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, moderator_id, reason)
        )
        await db.commit()

async def get_warn_count(guild_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM warns WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0
    
async def remove_warn(warn_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM warns WHERE id = ?",
            (warn_id,)
        )
        await db.commit()

async def get_warn(warn_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM warns WHERE id = ?",
            (warn_id,)
        )
        row = await cursor.fetchone()
        return row if row else None
    
async def get_warns(guild_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM warns WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        row = await cursor.fetchall()
        return row
    
async def get_autorole(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT autorole_id FROM config WHERE guild_id = ?",
            (guild_id,) 
        )
        row = await cursor.fetchone()

        return row[0] if row else None
import aiosqlite


async def init_db(database_name):
    """Creates the database and the users table."""
    async with aiosqlite.connect(database_name) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                gmt REAL DEFAULT '3.0',
                title TEXT DEFAULT 'Developer'
            )
        """)
        await conn.commit()


async def save_or_update_user(user_id, gmt, title, database_name):
    """Updates the user's information if the user exists, otherwise creates a new record (UPSERT)."""
    async with aiosqlite.connect(database_name) as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, gmt, title)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                gmt = excluded.gmt,
                title = excluded.title
        """,
            (user_id, gmt, title),
        )
        await conn.commit()


async def get_user(user_id, database_name):
    """Returns the user's information. Returns None if the user does not exist."""
    async with aiosqlite.connect(database_name) as conn:
        async with conn.execute(
            "SELECT gmt, title FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            result = await cursor.fetchone()

    if result:
        return {"gmt": result[0], "title": result[1]}
    return None

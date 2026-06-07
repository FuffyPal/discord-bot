import sqlite3

DB_NAME = "./database/database.db"


def init_db():
    """Creates the database and the users table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            gmt REAL DEFAULT '3.0',
            title TEXT DEFAULT 'Developer'
        )
    """)

    conn.commit()
    conn.close()


def save_or_update_user(user_id, gmt, title):
    """Updates the user's information if the user exists, otherwise creates a new record (UPSERT)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (user_id, gmt, title)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            gmt = excluded.gmt,
            title = excluded.title
    """,
        (user_id, gmt, title),
    )

    conn.commit()
    conn.close()


def get_user(user_id):
    """Returns the user's information. Returns None if the user does not exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT gmt, title FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return {"gmt": result[0], "title": result[1]}
    return None

import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()


def get_db_config():
    db_path = os.getenv("DB_PATH")
    db_name = os.getenv("DB_NAME")
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    return os.path.join(db_path, db_name)


def create_schema(db_full_path):
    try:
        conn = sqlite3.connect(db_full_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                game_name TEXT NOT NULL,
                total_time INTEGER DEFAULT 0,
                UNIQUE(guild_id, user_id, game_name)
            )
        """)
        conn.commit()
        print(f"Success: Database schema created at '{db_full_path}'.")
    except sqlite3.Error as e:
        print(f"Error: Could not create database: {e}")
    finally:
        if conn:
            conn.close()


def initialize_database():
    db_full_path = get_db_config()
    if os.path.exists(db_full_path):
        print("Info: Database already exists. Skipping initialization.")
        return
    create_schema(db_full_path)


if __name__ == "__main__":
    initialize_database()

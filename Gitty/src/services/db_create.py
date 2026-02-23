import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=dotenv_path)
DB_DIR = os.getenv("DB_DIR", "database")
DB_NAME = os.getenv("DB_NAME", "git_flow.db")

FINAL_DB_DIR = os.path.join(BASE_DIR, DB_DIR.replace("../", ""))
DB_PATH = os.path.join(FINAL_DB_DIR, DB_NAME)


def create_database():
    conn = None
    try:
        if not os.path.exists(FINAL_DB_DIR):
            os.makedirs(FINAL_DB_DIR)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Repositories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform VARCHAR(50),
                repo_name VARCHAR(255),
                star_count INTEGER,
                fork_count INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Repo_Stats (
                repo_id INTEGER,
                total_commits INTEGER,
                open_issues INTEGER,
                closed_issues INTEGER,
                open_prs INTEGER,
                closed_prs INTEGER,
                FOREIGN KEY (repo_id) REFERENCES Repositories(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Pipelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id INTEGER,
                status VARCHAR(20),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (repo_id) REFERENCES Repositories(id)
            )
        """)

        conn.commit()
        print("Hmm DATABASE: READY!")

    except sqlite3.Error as e:
        print(f"SQLite Errorr !!: {e}")
    except Exception as e:
        print(f"General Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_database()

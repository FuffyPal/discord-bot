import os
import sqlite3
from pathlib import Path

import gitlab
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

DB_DIR = os.getenv("DB_DIR", "database")
DB_NAME = os.getenv("DB_NAME", "git_flow.db")

FINAL_DB_DIR = (BASE_DIR / ".." / DB_DIR).resolve()
FINAL_DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = FINAL_DB_DIR / DB_NAME


def sync_gitlab_data():
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        print(f"❌ Error: GITLAB_TOKEN not found! {dotenv_path}")
        return

    gl = gitlab.Gitlab("https://gitlab.com", private_token=token)

    try:
        gl.auth()
        print(f"🚀 Fetching data for: {gl.user.username}")
        print(f"📂 Database Location: {DB_PATH}")

        conn = sqlite3.connect(str(DB_PATH))
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

        cursor.execute("DELETE FROM Repositories WHERE platform = 'gitlab'")

        projects = gl.projects.list(owned=True, all=True)

        repo_list = []
        for project in projects:
            repo_list.append(
                ("gitlab", project.name, project.star_count, project.forks_count)
            )

        cursor.executemany(
            "INSERT INTO Repositories (platform, repo_name, star_count, fork_count) VALUES (?, ?, ?, ?)",
            repo_list,
        )

        conn.commit()
        print(f"✅ {len(repo_list)} GitLab projects successfully saved.")

    except Exception as e:
        print(f"❌ Error: {e}")
        if "conn" in locals():
            conn.rollback()
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    sync_gitlab_data()

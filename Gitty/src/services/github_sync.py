import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from github import Auth, Github

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

DB_DIR = os.getenv("DB_DIR", "database")
DB_NAME = os.getenv("DB_NAME", "git_flow.db")

FINAL_DB_DIR = (BASE_DIR / ".." / DB_DIR).resolve()
FINAL_DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = FINAL_DB_DIR / DB_NAME


def sync_github_data():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print(f"❌ Error: GITHUB_TOKEN not found! Searched: {dotenv_path}")
        return

    auth = Auth.Token(token)
    g = Github(auth=auth)

    try:
        user = g.get_user()
        print(f"🚀 Fetching data for: {user.login}")
        print(f"📂 DB Location: {DB_PATH}")

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

        cursor.execute("DELETE FROM Repositories WHERE platform = 'github'")

        repos = user.get_repos()
        repo_list = []
        for repo in repos:
            repo_list.append(
                ("github", repo.name, repo.stargazers_count, repo.forks_count)
            )

        cursor.executemany(
            "INSERT INTO Repositories (platform, repo_name, star_count, fork_count) VALUES (?, ?, ?, ?)",
            repo_list,
        )

        conn.commit()
        print(f"✅ {len(repo_list)} repositories successfully saved to '{DB_NAME}'.")

    except Exception as e:
        print(f"❌ Error: {e}")
        if "conn" in locals():
            conn.rollback()
    finally:
        if "conn" in locals():
            conn.close()
        g.close()


if __name__ == "__main__":
    sync_github_data()

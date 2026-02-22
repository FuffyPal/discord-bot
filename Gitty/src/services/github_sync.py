import asyncio
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from github import Github, GithubException

BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = os.path.join(BASE_DIR, ".env")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv(
        dotenv_path=os.path.join(Path(__file__).resolve().parent.parent, ".env")
    )

DB_DIR = os.getenv("DB_DIR", "database")
DB_NAME = os.getenv("DB_NAME", "git_flow.db")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FINAL_DB_DIR = os.path.join(BASE_DIR, DB_DIR.replace("../", ""))
DB_PATH = os.path.join(FINAL_DB_DIR, DB_NAME)


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def process_single_repo(repo_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    repo_name, stars, forks = repo_data
    try:
        cursor.execute("SELECT id FROM Repositories WHERE repo_name = ?", (repo_name,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(
                "INSERT INTO Repositories (platform, repo_name, star_count, fork_count) VALUES (?, ?, ?, ?)",
                ("GitHub", repo_name, stars, forks),
            )
        else:
            cursor.execute(
                "UPDATE Repositories SET star_count = ?, fork_count = ? WHERE id = ?",
                (stars, forks, exists[0]),
            )
        conn.commit()
    finally:
        conn.close()


def process_single_issue(repo_info, g):
    r_id, r_name = repo_info
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        repo = g.get_repo(r_name)

        open_issues_list = repo.get_issues(state="open")
        closed_issues_list = repo.get_issues(state="closed")

        o_issue = sum(1 for i in open_issues_list if i.pull_request is None)
        c_issue = sum(1 for i in closed_issues_list if i.pull_request is None)

        cursor.execute("SELECT repo_id FROM Repo_Stats WHERE repo_id = ?", (r_id,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE Repo_Stats SET open_issues = ?, closed_issues = ? WHERE repo_id = ?",
                (o_issue, c_issue, r_id),
            )
        else:
            cursor.execute(
                "INSERT INTO Repo_Stats (repo_id, open_issues, closed_issues, total_commits) VALUES (?, ?, ?, 0)",
                (r_id, o_issue, c_issue),
            )
        conn.commit()
    except GithubException:
        print(f"Warning: {r_name} Issue error (404/403).")
    finally:
        conn.close()


def process_single_commit(repo_info, g):
    r_id, r_name = repo_info
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        repo = g.get_repo(r_name)
        count = repo.get_commits().totalCount
        cursor.execute(
            "UPDATE Repo_Stats SET total_commits = ? WHERE repo_id = ?", (count, r_id)
        )
        conn.commit()
    except GithubException:
        print(f"Warning: {r_name} Commit error (Empty repo).")
    finally:
        conn.close()


def process_single_pr(repo_info, g):
    r_id, r_name = repo_info
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        repo = g.get_repo(r_name)

        open_prs_list = repo.get_pulls(state="open")
        closed_prs_list = repo.get_pulls(state="closed")

        o_pr = open_prs_list.totalCount
        c_pr = closed_prs_list.totalCount

        cursor.execute("SELECT repo_id FROM Repo_Stats WHERE repo_id = ?", (r_id,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE Repo_Stats SET open_prs = ?, closed_prs = ? WHERE repo_id = ?",
                (o_pr, c_pr, r_id),
            )
        else:
            cursor.execute(
                "INSERT INTO Repo_Stats (repo_id, open_prs, closed_prs, total_commits, open_issues, closed_issues) "
                "VALUES (?, ?, ?, 0, 0, 0)",
                (r_id, o_pr, c_pr),
            )
        conn.commit()
    except GithubException:
        print(f"Warning: {r_name} PR error (404/403).")
    finally:
        conn.close()


async def run_parallel(func, items, *args):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [loop.run_in_executor(executor, func, item, *args) for item in items]
        await asyncio.gather(*tasks)


async def main():
    if not GITHUB_TOKEN or not os.path.exists(DB_PATH):
        print("Error: Token or DB not found.")
        return

    g = Github(GITHUB_TOKEN, timeout=15, retry=None)

    try:
        print("Stage 1: Synchronizing GitHub repositories...")
        # get_user().get_repos() çağrısını try-except içine alıyoruz
        user_repos = [
            (r.full_name, r.stargazers_count, r.forks_count)
            for r in g.get_user().get_repos()
        ]
        await run_parallel(process_single_repo, user_repos)

        conn = get_db_connection()
        # Sadece GitHub repolarını güncellemek için WHERE platform='GitHub' ekledik
        db_repos = conn.execute(
            "SELECT id, repo_name FROM Repositories WHERE platform='GitHub'"
        ).fetchall()
        conn.close()

        print("Stage 2: Fetching issue data...")
        await run_parallel(process_single_issue, db_repos, g)

        print("Stage 3: Fetching commit data...")
        await run_parallel(process_single_commit, db_repos, g)

        print("Stage 4: Fetching pull request data...")
        await run_parallel(process_single_pr, db_repos, g)

    except GithubException as e:
        print(f"❌ GitHub API Error (Rate Limit or Auth): {e}")
    except Exception as e:
        print(f"❌ General GitHub Sync Error: {e}")

    print("Operation Successful: Repositories, Issues, and Commits synchronized.")


def sync_github_data():
    """Main.py'nin thread içinde güvenle çağırabilmesi için giriş noktası"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()


if __name__ == "__main__":
    sync_github_data()

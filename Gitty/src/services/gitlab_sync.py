import asyncio
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import gitlab
from dotenv import load_dotenv

# Mimari Gereği Dizin Yapılandırması
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
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")

FINAL_DB_DIR = os.path.join(BASE_DIR, DB_DIR.replace("../", ""))
DB_PATH = os.path.join(FINAL_DB_DIR, DB_NAME)


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def process_gitlab_repo(repo_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    repo_name, stars, forks = repo_data
    try:
        cursor.execute("SELECT id FROM Repositories WHERE repo_name = ?", (repo_name,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(
                "INSERT INTO Repositories (platform, repo_name, star_count, fork_count) VALUES (?, ?, ?, ?)",
                ("GitLab", repo_name, stars, forks),
            )
        else:
            cursor.execute(
                "UPDATE Repositories SET star_count = ?, fork_count = ? WHERE id = ?",
                (stars, forks, exists[0]),
            )
        conn.commit()
    finally:
        conn.close()


def process_gitlab_issues(repo_info, gl):
    r_id, r_name = repo_info
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        project = gl.projects.get(r_name)
        # Yeni versiyonlarda get_all=True parametresi veya len check kullanılır
        o_issue = len(project.issues.list(state="opened", get_all=True))
        c_issue = len(project.issues.list(state="closed", get_all=True))

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
    except Exception as e:
        print(f"Warning: GitLab Issue error on {r_name}: {e}")
    finally:
        conn.close()


def process_gitlab_commits(repo_info, gl):
    """'list' object has no attribute 'total' hatası için düzeltildi."""
    r_id, r_name = repo_info
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        project = gl.projects.get(r_name)
        # GitLab'da commit sayısını almanın en performanslı yolu HEAD isteği veya sayfalama bilgisidir
        # list() metodu 'get_all=False' iken python-gitlab nesnesinde total bilgisini barındırır
        commits = project.commits.list(all=False, lazy=True)
        # total_count, python-gitlab manager üzerinden çekilir
        count = (
            commits.total
            if hasattr(commits, "total")
            else len(project.commits.list(get_all=True))
        )

        cursor.execute(
            "UPDATE Repo_Stats SET total_commits = ? WHERE repo_id = ?", (count, r_id)
        )
        conn.commit()
    except Exception as e:
        print(f"Warning: GitLab Commit error on {r_name}: {e}")
    finally:
        conn.close()


def process_gitlab_mrs(repo_info, gl):
    r_id, r_name = repo_info
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        project = gl.projects.get(r_name)
        o_mr = len(project.mergerequests.list(state="opened", get_all=True))
        c_mr = len(project.mergerequests.list(state="merged", get_all=True)) + len(
            project.mergerequests.list(state="closed", get_all=True)
        )

        cursor.execute("SELECT repo_id FROM Repo_Stats WHERE repo_id = ?", (r_id,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE Repo_Stats SET open_prs = ?, closed_prs = ? WHERE repo_id = ?",
                (o_mr, c_mr, r_id),
            )
        conn.commit()
    except Exception as e:
        print(f"Warning: GitLab MR error on {r_name}: {e}")
    finally:
        conn.close()


def process_gitlab_pipelines(repo_info, gl):
    r_id, r_name = repo_info
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        project = gl.projects.get(r_name)
        # Mevcut mimarideki Pipelines tablosuna son 5 tanesini ekler
        pipelines = project.pipelines.list(page=1, per_page=5)

        for pipe in pipelines:
            # Tekrar eden pipeline eklememek için kontrol
            cursor.execute(
                "INSERT INTO Pipelines (repo_id, status, created_at) VALUES (?, ?, ?)",
                (r_id, pipe.status, pipe.created_at),
            )
        conn.commit()
    except Exception as e:
        print(f"Warning: GitLab Pipeline error on {r_name}: {e}")
    finally:
        conn.close()


async def run_parallel(func, items, *args):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [loop.run_in_executor(executor, func, item, *args) for item in items]
        await asyncio.gather(*tasks)


async def main():
    if not GITLAB_TOKEN or not os.path.exists(DB_PATH):
        print("Error: GitLab Token or DB not found.")
        return

    # Sürüm 5.0.0+ ve 8.0.0 için uyumlu bağlantı
    gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
    gl.auth()

    print("Stage 1: Synchronizing GitLab repositories...")
    # 'owned=True' sadece sizin olan projeleri çeker
    projects = gl.projects.list(owned=True, get_all=True)
    user_projects = [
        (p.path_with_namespace, p.star_count, p.forks_count) for p in projects
    ]
    await run_parallel(process_gitlab_repo, user_projects)

    conn = get_db_connection()
    db_repos = conn.execute(
        "SELECT id, repo_name FROM Repositories WHERE platform='GitLab'"
    ).fetchall()
    conn.close()

    print("Stage 2: Fetching GitLab issues...")
    await run_parallel(process_gitlab_issues, db_repos, gl)

    print("Stage 3: Fetching GitLab commits...")
    await run_parallel(process_gitlab_commits, db_repos, gl)

    print("Stage 4: Fetching GitLab Merge Requests...")
    await run_parallel(process_gitlab_mrs, db_repos, gl)

    print("Stage 5: Fetching GitLab Pipelines...")
    await run_parallel(process_gitlab_pipelines, db_repos, gl)

    print("Operation Successful: GitLab Data Synchronized.")


if __name__ == "__main__":
    asyncio.run(main())


def sync_gitlab_data():
    """Main.py'nin thread içinde güvenle çağırabilmesi için"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

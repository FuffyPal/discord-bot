import asyncio
import os
import sqlite3

from services.db_create import DB_PATH, create_database
from services.github_sync import sync_github_data
from services.gitlab_sync import sync_gitlab_data
from services.webhook import notifier


def get_current_stats():
    stats = {}
    if not os.path.exists(DB_PATH):
        return stats

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT platform, repo_name, star_count, fork_count FROM Repositories"
        )
        for row in cursor.fetchall():
            key = f"{row['platform']}_{row['repo_name']}"
            stats[key] = {
                "stars": int(row["star_count"]),
                "forks": int(row["fork_count"]),
            }
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()
    return stats


async def run_sync_loop():
    print("🚀 Gitty Active! Parallel check starting every 10000 seconds...")

    while True:
        old_stats = get_current_stats()

        print("🔄 Updating data asynchronously...")
        await asyncio.gather(
            asyncio.to_thread(sync_github_data), asyncio.to_thread(sync_gitlab_data)
        )

        new_stats = get_current_stats()

        for repo_key, data in new_stats.items():
            platform, repo_name = repo_key.split("_", 1)

            if repo_key in old_stats:
                old = old_stats[repo_key]
                star_diff = data["stars"] - old["stars"]
                fork_diff = data["forks"] - old["forks"]

                if star_diff > 0 or fork_diff > 0:
                    msg = f"**{repo_name}** ({platform.upper()})\n"
                    if star_diff > 0:
                        msg += f"🌟 Yıldız arttı: {old['stars']} ➡️ {data['stars']}\n"
                    if fork_diff > 0:
                        msg += f"🍴 Fork arttı: {old['forks']} ➡️ {data['forks']}"

                    await notifier.send_embed(
                        category="stats",
                        title="📈 Repo Güncellemesi",
                        description=msg,
                        color=0x3498DB,
                    )
                    print(f"✅ Notification sent for {repo_name}.")
            else:
                await notifier.send_embed(
                    category="stats",
                    title="🆕 Yeni Repo Takibi",
                    description=f"**{repo_name}** ({platform.upper()}) veritabanına eklendi.",
                    color=0x2ECC71,
                )

        print("😴 Waiting for 1000 seconds...")
        await asyncio.sleep(1000)


async def main():
    print("🛠️  STEP 1: Preparing database...")
    create_database()

    await run_sync_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 System shut down by user.")

import asyncio
import os
import sys
import time

# Yol tanımlamaları
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.db_create import create_database
from services.github_sync import main as github_main
from services.gitlab_sync import main as gitlab_main
from services.webhook import notifier

SYNC_INTERVAL = 1000


async def run_forever():
    print("--- Gitty Sync Engine Started ---")
    create_database()

    while True:
        start_time = time.time()
        print(f"\n[Cycle Start] {time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            await asyncio.wait_for(
                asyncio.gather(github_main(), gitlab_main(), return_exceptions=True),
                timeout=600,
            )

        except asyncio.TimeoutError:
            print("[Error] Sync timed out!")
        except Exception as e:
            print(f"[Critical Error] {e}")
            await notifier.send_embed(
                "updates", "❌ Hata Oluştu", str(e), color=0xE74C3C
            )

        elapsed = time.time() - start_time
        sleep_time = max(10, SYNC_INTERVAL - elapsed)  # En az 10 saniye bekle

        print(f"[Cycle Finished] Sleeping for {int(sleep_time)} seconds...")
        await asyncio.sleep(sleep_time)  # BU SATIR YENİ DÖNGÜYÜ TETİKLER


if __name__ == "__main__":
    try:
        asyncio.run(run_forever())
    except KeyboardInterrupt:
        print("\nStopped.")

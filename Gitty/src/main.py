import asyncio
import os
import sys
import time

# Mimari gereği path düzenlemesi
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.db_create import create_database
from services.github_sync import main as github_main
from services.gitlab_sync import main as gitlab_main
from services.webhook import notifier

# Test amaçlı 10 saniyeye ayarlandı
SYNC_INTERVAL = 10


async def run_forever():
    print("--- Gitty Continuous Sync Engine Started (Fast Mode) ---")

    # Veritabanı kontrolü başlangıçta bir kez yapılır
    create_database()

    while True:
        start_time = time.time()
        print(f"\n[Cycle Start] {time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Platform senkronizasyonlarını paralel başlatıyoruz
            # return_exceptions=True: Bir platform hata alsa da diğeri devam eder
            results = await asyncio.gather(
                github_main(), gitlab_main(), return_exceptions=True
            )

            # Sonuçları kontrol et ve hataları bildir
            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    platform = "GitHub" if i == 0 else "GitLab"
                    print(f"Critical Error in {platform}: {res}")
                    # Discord üzerinden hata bildirimi gönderilir
                    await notifier.send_embed(
                        "updates",
                        f"{platform} Sync Error",
                        f"Loop failed for {platform}: {str(res)}",
                        color=0xE74C3C,
                    )

        except Exception as e:
            print(f"General Loop Error: {e}")

        # Süre hesaplama: İşlem süresini belirlenen aralıktan çıkarır
        elapsed = time.time() - start_time
        sleep_time = max(0, SYNC_INTERVAL - elapsed)

        print(f"[Cycle Finished] Elapsed: {elapsed:.2f}s. Waiting {sleep_time:.2f}s...")
        await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    try:
        asyncio.run(run_forever())
    except KeyboardInterrupt:
        print("\n[Service Stopped] Terminated by user.")

import asyncio
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from services.db_create import DB_PATH, create_database
from services.github_sync import sync_github_data
from services.gitlab_sync import sync_gitlab_data
from services.webhook import notifier

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_current_stats():
    """Repositories ve Repo_Stats tablolarından tüm verileri al"""
    stats = {}
    if not os.path.exists(DB_PATH):
        print("❌ DB yok!")
        return stats

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Önce tüm repoları al
        cursor.execute("""
            SELECT id, platform, repo_name, star_count, fork_count
            FROM Repositories
        """)
        repos = cursor.fetchall()

        # Her repo için temel verileri ekle
        repo_map = {}  # id -> key mapping
        for repo in repos:
            key = f"{repo['platform']}_{repo['repo_name']}"
            repo_map[repo["id"]] = key
            stats[key] = {
                "stars": int(repo["star_count"]),
                "forks": int(repo["fork_count"]),
                "commits": 0,
                "open_issues": 0,
                "closed_issues": 0,
                "open_prs": 0,
                "closed_prs": 0,
            }

        # Repo_Stats verilerini al
        if repos:  # Eğer hiç repo yoksa sorgu yapma
            repo_ids = [r["id"] for r in repos]
            placeholders = ",".join(["?"] * len(repo_ids))

            cursor.execute(
                f"""
                SELECT repo_id, total_commits, open_issues, closed_issues,
                       open_prs, closed_prs
                FROM Repo_Stats
                WHERE repo_id IN ({placeholders})
            """,
                repo_ids,
            )

            for row in cursor.fetchall():
                key = repo_map.get(row["repo_id"])
                if key and key in stats:
                    stats[key]["commits"] = row["total_commits"] or 0
                    stats[key]["open_issues"] = row["open_issues"] or 0
                    stats[key]["closed_issues"] = row["closed_issues"] or 0
                    stats[key]["open_prs"] = row["open_prs"] or 0
                    stats[key]["closed_prs"] = row["closed_prs"] or 0

    except sqlite3.OperationalError as e:
        print(f"⚠️ Veritabanı hatası (ilk çalıştırmada normal): {e}")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
    finally:
        conn.close()

    return stats


def compare_stats(old, new):
    """İki stats arasındaki farkları bul ve mesaj oluştur"""
    changes = []

    # Yıldız kontrolü
    if new["stars"] != old["stars"]:
        changes.append(f"🌟 Yıldız: {old['stars']} ➡️ {new['stars']}")

    # Fork kontrolü
    if new["forks"] != old["forks"]:
        changes.append(f"🍴 Fork: {old['forks']} ➡️ {new['forks']}")

    # Commit kontrolü
    if new["commits"] != old["commits"]:
        changes.append(f"📝 Commit: {old['commits']} ➡️ {new['commits']}")

    # Issue kontrolü
    if new["open_issues"] != old["open_issues"]:
        changes.append(f"🐛 Açık Issue: {old['open_issues']} ➡️ {new['open_issues']}")
    if new["closed_issues"] != old["closed_issues"]:
        changes.append(
            f"✅ Kapanan Issue: {old['closed_issues']} ➡️ {new['closed_issues']}"
        )

    # PR kontrolü
    if new["open_prs"] != old["open_prs"]:
        changes.append(f"🔀 Açık PR: {old['open_prs']} ➡️ {new['open_prs']}")
    if new["closed_prs"] != old["closed_prs"]:
        changes.append(f"🔀 Kapanan PR: {old['closed_prs']} ➡️ {new['closed_prs']}")

    return changes


async def send_with_delay(notifier_func, delay=1.0):
    """Webhook mesajını gönder ve belirtilen süre bekle (rate limit koruması)"""
    result = await notifier_func
    await asyncio.sleep(delay)
    return result


async def run_sync_loop():
    print("🚀 Gitty Active! Parallel check starting every 1000 seconds...")
    print(
        "📊 Tüm repo istatistikleri (yıldız, fork, commit, issue, PR) takip ediliyor..."
    )
    print("⏱️  Rate limit koruması: Her mesajdan sonra 1 saniye beklenecek")

    # İlk çalıştırmada mevcut verileri göster
    initial_stats = get_current_stats()
    print(f"📈 Başlangıçta {len(initial_stats)} repo takip ediliyor.")

    while True:
        try:
            # 1. Güncelleme öncesi veriler
            old_stats = get_current_stats()
            print(f"🔄 Güncelleme başlıyor... ({len(old_stats)} repo)")

            # 2. GitHub ve GitLab'dan verileri çek
            print("  ⚙️ GitHub senkronizasyonu...")
            try:
                await asyncio.to_thread(sync_github_data)
            except Exception as e:
                print(f"  ⚠️ GitHub Sync hatası (devam ediliyor): {e}")

            print("  ⚙️ GitLab senkronizasyonu...")
            try:
                await asyncio.to_thread(sync_gitlab_data)
            except Exception as e:
                print(f"  ⚠️ GitLab Sync hatası (devam ediliyor): {e}")

            # 3. Güncelleme sonrası veriler
            new_stats = get_current_stats()
            print(f"✅ Güncelleme tamamlandı. ({len(new_stats)} repo)")

            # 4. Değişiklikleri kontrol et ve bildirim gönder
            notification_count = 0

            # Yeni eklenen repolar
            for repo_key in new_stats:
                if repo_key not in old_stats:
                    platform, repo_name = repo_key.split("_", 1)
                    data = new_stats[repo_key]

                    # Yeni repo mesajı oluştur
                    msg = f"**{repo_name}** ({platform.upper()})\n"
                    msg += f"🌟 {data['stars']} yıldız, 🍴 {data['forks']} fork"

                    if data["commits"] > 0:
                        msg += f"\n📝 {data['commits']} commit"
                    if data["open_issues"] > 0 or data["closed_issues"] > 0:
                        msg += f"\n🐛 {data['open_issues']} açık / ✅ {data['closed_issues']} kapalı issue"
                    if data["open_prs"] > 0 or data["closed_prs"] > 0:
                        msg += f"\n🔀 {data['open_prs']} açık / 🔀 {data['closed_prs']} kapalı PR"

                    await send_with_delay(
                        notifier.send_embed(
                            category="stats",
                            title="🆕 Yeni Repo Takibe Alındı",
                            description=msg,
                            color=0x2ECC71,  # Yeşil
                        ),
                        delay=1.0,  # 1 saniye bekle
                    )
                    notification_count += 1
                    print(f"  📨 Yeni repo bildirimi: {repo_name}")

            # Varolan repolardaki değişiklikler
            for repo_key in old_stats:
                if repo_key in new_stats:
                    old = old_stats[repo_key]
                    new = new_stats[repo_key]

                    changes = compare_stats(old, new)

                    if changes:
                        platform, repo_name = repo_key.split("_", 1)
                        msg = f"**{repo_name}** ({platform.upper()})\n" + "\n".join(
                            changes
                        )

                        await send_with_delay(
                            notifier.send_embed(
                                category="stats",
                                title="📊 Repo Güncellemesi",
                                description=msg,
                                color=0x3498DB,  # Mavi
                            ),
                            delay=1.0,  # 1 saniye bekle
                        )
                        notification_count += 1
                        print(
                            f"  📨 Güncelleme bildirimi: {repo_name} ({len(changes)} değişiklik)"
                        )

            if notification_count == 0:
                print("  ℹ️ Değişiklik yok, bildirim gönderilmedi.")
            else:
                print(
                    f"  ✅ {notification_count} bildirim gönderildi. (Her biri arasında 1 saniye beklendi)"
                )

            # 5. Bekleme
            print("😴 1000 saniye bekleniyor... (16.6 dakika)")
            await asyncio.sleep(7000)

        except KeyboardInterrupt:
            print("\n🛑 Kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            print("😴 60 saniye sonra yeniden deneniyor...")
            await asyncio.sleep(60)


async def main():
    print("🛠️  ADIM 1: Veritabanı hazırlanıyor...")
    create_database()

    print("🤖 Gitty Bot başlatılıyor...")
    print("📨 Webhook bildirimleri aktif")

    # Webhook test mesajı (isteğe bağlı)
    try:
        await send_with_delay(
            notifier.send_embed(
                category="stats",
                title="🚀 Gitty Bot Aktif",
                description="Repo takibi başladı! Tüm değişiklikler bildirilecek.\n⏱️ Rate limit koruması: 2 saniye",
                color=0x9B59B6,  # Mor
            ),
            delay=2.0,
        )
        print("✅ Test bildirimi gönderildi.")
    except Exception as e:
        print(f"⚠️ Test bildirimi gönderilemedi: {e}")

    await run_sync_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Sistem kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Kritik hata: {e}")

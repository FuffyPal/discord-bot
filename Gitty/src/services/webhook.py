import asyncio
import os
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))


class DiscordNotifier:
    def __init__(self):
        self.webhooks = {
            "stats": os.getenv("WEBHOOK_STATS", "").strip(),
            "updates": os.getenv("WEBHOOK_UPDATES", "").strip(),
            "pipelines": os.getenv("WEBHOOK_PIPELINES", "").strip(),
        }
        print("🔍 Webhook URLs yüklendi:")
        for k, v in self.webhooks.items():
            print(f"  {k}: {v if v else '❌ BOŞ'}")

    async def send_embed(self, category, title, description, color=0x3498DB):
        url = self.webhooks.get(category)  # ÖNCE url'yi tanımla
        print(f"[DEBUG] Sending to {category}: {url}")  # SONRA yazdır

        if not url or not url.startswith("https"):
            print(f"❌ {category} webhook URL geçersiz veya boş")
            return False

        payload = {
            "embeds": [
                {
                    "title": title,
                    "description": description,
                    "color": color,
                    "footer": {"text": "Gitty Bot - Database Sync"},
                }
            ]
        }

        try:
            headers = {"Content-Type": "application/json"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status in [200, 204]:
                        print(f"✅ Webhook başarılı: {category}")
                        return True
                    else:
                        print(f"❌ Webhook hatası {resp.status}: {await resp.text()}")
                        return False
        except Exception as e:
            print(f"❌ Webhook bağlantı hatası: {e}")
            return False


notifier = DiscordNotifier()

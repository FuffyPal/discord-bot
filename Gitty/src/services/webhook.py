import asyncio
import os
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

# Mevcut yol yapılandırması aynı kalacak...
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))


class DiscordNotifier:
    def __init__(self):
        self.webhooks = {
            "stats": os.getenv("WEBHOOK_STATS", "").strip(),
            "updates": os.getenv("WEBHOOK_UPDATES", "").strip(),
            "pipelines": os.getenv("WEBHOOK_PIPELINES", "").strip(),
        }

    async def send_embed(self, category, title, description, color=0x3498DB):
        url = self.webhooks.get(category)
        if not url or not url.startswith("https"):
            return

        # Discord Webhook JSON formatı
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
                        return True
                    else:
                        print(
                            f"Webhook Error: Status {resp.status} - {await resp.text()}"
                        )
        except Exception as e:
            print(f"Webhook Connection Error: {e}")


notifier = DiscordNotifier()

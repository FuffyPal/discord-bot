import asyncio
import os

import aiohttp
from discord import Embed, Webhook
from dotenv import load_dotenv

load_dotenv()


class DiscordNotifier:
    def __init__(self):
        self.urls = {
            "stats": os.getenv("WEBHOOK_STATS", "").strip(),
            "updates": os.getenv("WEBHOOK_UPDATES", "").strip(),
            "pipelines": os.getenv("WEBHOOK_PIPELINES", "").strip(),
        }
        self._lock = asyncio.Lock()

    async def send_embed(self, category, title, description, color=0x3498DB):
        url = self.urls.get(category)
        if not url or not url.startswith("https://"):
            return

        async with self._lock:
            async with aiohttp.ClientSession() as session:
                attempts = 0
                while attempts < 3:
                    try:
                        webhook = Webhook.from_url(url, session=session)
                        embed = Embed(title=title, description=description, color=color)
                        embed.set_footer(text="Gitty Bot - Database Sync")

                        await webhook.send(embed=embed)

                        print(f"⏳ Message sent ({category}). Waiting 2s for safety...")
                        await asyncio.sleep(2)
                        return True

                    except Exception as e:
                        attempts += 1
                        print(f"⚠️ Discord Error (Attempt {attempts}): {e}")
                        await asyncio.sleep(5 * attempts)

                return False


notifier = DiscordNotifier()

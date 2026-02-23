import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # .env dosyasını yükle [cite: 3]
intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN")
# .env'den gelen string değeri int'e çeviriyoruz
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))


@bot.event
async def on_ready():
    print(f"Bot {bot.user} aktif!")
    await join_channel()


async def join_channel():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            await channel.connect()
            print(f"{channel.name} kanalına girildi.")
        except Exception as e:
            print(f"Bağlantı hatası: {e}")


@bot.event
async def on_voice_state_update(member, before, after):
    # Eğer bot kanaldan atılırsa veya kanal silinirse geri döner
    if member.id == bot.user.id and after.channel is None:
        print("Kanal kapandı veya atıldım, tekrar bağlanıyorum...")
        await join_channel()


bot.run(TOKEN)

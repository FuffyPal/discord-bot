import asyncio
import os

import discord
from Cogs.commands import setup_commands
from database_create import initialize_database
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
initialize_database()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = discord.Object(id=int(os.getenv("Developer_servver")))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">>", intents=intents)

setup_commands(bot, GUILD_ID)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=GUILD_ID)
        print(f"Synced {len(synced)} commands to the development server.")
    except Exception as e:
        print(f"Sync error: {e}")


async def main():
    async with bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down bot...")

from dotenv import load_dotenv
load_dotenv()

import discord
import os
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

TOKEN = os.getenv("TOKEN")

bot = discord.Bot()

@bot.slash_command()
async def hello(ctx, name: str = None, nachricht: str = None):
    name = name or ctx.author.name
    if nachricht == None:
        await ctx.respond(f"Hello {name}")
    else:
        await ctx.respond(f"Hello {name}, {nachricht}")

@bot.user_command(name="Say Hello")
async def hi(ctx, user):
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")

@bot.message_command(nachricht="Bla Bla ...")
async def hi(ctx, nachricht):
    await ctx.respond(f"{ctx.message.content} says bla bla to {nachricht}!")

bot.run(TOKEN)

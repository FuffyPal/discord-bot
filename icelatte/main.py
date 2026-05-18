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

@bot.slash_command()
async def say(ctx, nachricht: str = None, mention_author: bool = True):
    nachricht = nachricht or ""
    if mention_author:
        await ctx.respond(f"{ctx.author.mention} says: {nachricht}")
    else:
        await ctx.respond(f"{ctx.author.name} says: {nachricht}")

@bot.slash_command()
async def invate(ctx):
    await ctx.respond("Invate Mee yeyy:\nhttps://discord.com/oauth2/authorize?client_id=1505951400281247825&permissions=4503599627373568&integration_type=0&scope=bot")
        
@bot.user_command(name="Say Hello")
async def hi(ctx, user):
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")


bot.run(TOKEN)

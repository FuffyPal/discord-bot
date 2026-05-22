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
owner=int(os.getenv("OWNER"))
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} successfully logged in!")


@bot.slash_command()
async def hello(
    ctx, 
    name: str = None, 
    nachricht: str = None
    ):

    name = name or ctx.author.name
    if nachricht == None:
        await ctx.respond(f"Hello {name}")
    else:
        await ctx.respond(f"Hello {name}, {nachricht}")

@bot.slash_command()
async def say(
    ctx, 
    nachricht: str = None, 
    mention_author: bool = True
    ):

    nachricht = nachricht or ""
    if mention_author:
        await ctx.respond(f"{ctx.author.mention} says: {nachricht}")
    else:
        await ctx.respond(f"{ctx.author.name} says: {nachricht}")

@bot.slash_command()
async def say_embed(
    ctx, 
    nachricht: str = None
    ):

    nachricht = nachricht or ""
    await ctx.respond(embed = discord.Embed(
        title=ctx.author.name+": Says",
        description=nachricht,
        color=0x74456e
    ))

@bot.slash_command()
async def invate(
    ctx
    ):

    await ctx.respond("Invate Mee yeyy:\nhttps://discord.com/oauth2/authorize?client_id=1505951400281247825&permissions=4503599627373568&integration_type=0&scope=bot")
        
@bot.slash_command(
    name="testembed", 
    description="test embed."
    )
async def testembed(
    ctx
    ):

    embed = discord.Embed(
        title="Test Embed",
        description="Das ist ein Test Embed.",
        color=0x74456e
    )
    await ctx.respond(embed=embed)

@bot.slash_command(
    name="stop", 
    description="Stops the bot."
    )

async def stop(
    ctx
    ):

    user_id = ctx.author.id
    if user_id == owner:
        embed = discord.Embed(
            title="Stop",
            description="Bot stopped.",
            color=0x25323d
        )
        await ctx.respond(embed=embed)
        exit()
    else:
        embed = discord.Embed(
            title="Access denied",
            description="You're not allowed to use this command!",
            color=0x25323d
        )
        await ctx.respond(embed=embed)

@bot.user_command(
    name="Say Hello"
    )

async def hi(
    ctx, 
    user
    ):

    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")
    
bot.run(TOKEN)

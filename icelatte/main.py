from dotenv import load_dotenv
load_dotenv()

import discord
import os

import logging

token = os.getenv("TOKEN")
owner=int(os.getenv("OWNER"))
debug=int(os.getenv("DEBUG"))
bot = discord.Bot()

logger = logging.getLogger('discord')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

if debug == 1:
    logger.setLevel(logging.DEBUG)
    logger.debug("debug mode DEBUG!")
    print("DEBUG is set to 1 (DEBUG mode)")

elif debug == 2:
    logger.setLevel(logging.ERROR)
    logger.error("debug mode ERROR!")
    print("DEBUG is set to 2 (ERROR mode)")

elif debug == 3:
    logger.setLevel(logging.INFO)
    logger.info("debug mode INFO!")
    print("DEBUG is set to 3 (INFO mode)")

elif debug == 4:
    logger.setLevel(logging.WARNING)
    logger.warning("debug mode WARNING!")
    print("DEBUG is set to 4 (WARNING mode)")

elif debug == 5:
    logger.setLevel(logging.CRITICAL)
    logger.critical("debug mode CRITICAL!")
    print("DEBUG is set to 5 (CRITICAL mode)")

else:
    logger.setLevel(logging.NOTSET)
    print("DEBUG is not set!")

@bot.event
async def on_ready():
    print(f"{bot.user} successfully logged in!")


@bot.slash_command(
    name="hello",
    description="Says hello to the user."
)
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

@bot.slash_command(
    name="say",
    description="Repeats the message sent by the user."
)

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

@bot.slash_command(
    name="say_embed",
    description="Repeats the message inside an embed."
)

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

@bot.slash_command(
    name="invite", 
    description="Invate the bot to your server. and get a invite for my server"
    )
async def invate(
    ctx
    ):

    embed = discord.Embed(
        title="Invite Mee yeyy",
        description="[Invite Mee!](https://discord.com/oauth2/authorize?client_id=1505951400281247825&permissions=4503599627373568&integration_type=0&scope=bot)\n[My server!](https://discord.gg/qsQxHk2V8c)",
        color=0x74456e
    )
    await ctx.respond(embed=embed)

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
@bot.slash_command(
    name="ping", 
    description="Measures latency between the server and a given IP."
    )

async def ping(
    ctx,
    ip: str = None,
    count: int = None
    ):
    await ctx.defer()
    
    ip = ip or "1.1.1.1"
    count = count or 3
    from src.ping import ping
    result = ping(ip, count)
    embed = discord.Embed(
        title="Ping",
        description=result,
        color=0x1a3d65
    )
    await ctx.respond(embed=embed)

@bot.slash_command(
    name="palc", 
    description="Palisch Language Converter :3"
    )

async def palc(
    ctx,
    text: str = None,
    embed: bool = True
    ):
    await ctx.defer()
    
    text = text or ""
    from src.palc import convert_text
    result = convert_text(text)

    if embed == True:
        embed = discord.Embed(
            title="Pal Cutiee Lang :3",
            description=result,
            color=0x1a3d65
        )
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(result)


@bot.user_command(
    name="Say Hello"
    )

async def hi(
    ctx, 
    user
    ):

    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")
    
bot.run(token)

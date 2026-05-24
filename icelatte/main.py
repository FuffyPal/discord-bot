from dotenv import load_dotenv
load_dotenv()

import discord
import os

import logging
import datetime

from src.storage import init_db

init_db()

token = os.getenv("TOKEN")
me=int(966300934202359888)
debug=int(os.getenv("DEBUG", 0))
bot = discord.Bot()

logger = logging.getLogger('discord')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Colours
purple=0x74456e
dark_blue=0x1a3d65
grey=0x25323d
purple_2=0x9c18a3
pink=0xc586c0

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

debug_modes = {
    1: ("DEBUG mode", "<:DebugBug1:1507752466152947822>"),
    2: ("ERROR mode", ":x:"),
    3: ("INFO mode", "<:dieinfo:1507752914465325066>"),
    4: ("WARNING mode", "<:warning:1507753301687537755>"),
    5: ("CRITICAL mode", ":warning:")
}

mode_name, emoji = debug_modes.get(debug, ("not set", "❓"))

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
    name="register",
    description="Say this to register for Timezone and title."
)
@discord.option(
    name="gmt",
    description="Enter your GMT offset (e.g., 3 for Turkey, -5 for New York)",
    type=float,
    min_value=-12.0,
    max_value=14.0,
    required=True
)
@discord.option(
    name="title",
    description="Enter your title (e.g., Developer, jhonny, student, etc)",
    type=str,
    required=True
)
async def register(
    ctx, 
    gmt: str = None, 
    title: str = None
    ):

    if gmt == None:
        await ctx.respond(f"You need to provide a timezone!")
    elif title == None:
        await ctx.respond(f"You need to provide a title!")
    elif gmt == None and title == None:
        await ctx.respond(f"You need to provide a timezone and title!")
    else:
        from src.storage import save_or_update_user
        user_id = ctx.author.id
        save_or_update_user(user_id, gmt, title)
        await ctx.respond(f"You provided a timezone and title! {user_id}")
        
@bot.slash_command(
    name="get_user_info",
    description="Displays profile information about the user."
)
@discord.option(
    name="user_id",
    description="Enter the user ID (e.g., 123456789)",
    type=str,
    required=True
)
async def get_user_info(
    ctx,
    user_id: str = None
    ):
    user_id_access = ctx.author.id
    if user_id_access == me:
        if user_id == None:
            await ctx.respond(f"You need to provide a ID!")
        else:
            try:
                user_id_int = int(user_id)
            except ValueError:
                await ctx.respond("Please enter a valid numeric ID!")
                return
            from src.storage import get_user
            result = get_user(user_id_int)
            if result:
                await ctx.respond(f"GMT: {result['gmt']}, Title: {result['title']}")
            else:
                await ctx.respond("User not found!")
    else:
        await ctx.respond("You're not allowed to use this command!")
            
@bot.slash_command(
    name="whoami",
    description="Displays profile information about you."
)

async def whoami(
    ctx
    ):
    
    from src.storage import get_user
    user_id = ctx.author.id
    result = get_user(user_id)
    
    if result:
        await ctx.respond(f"GMT: {result['gmt']}, Title: {result['title']}")
    else:
        await ctx.respond("User not found!")

@bot.slash_command(
    name="say_time",
    description="Displays the time in GMT."
)

async def say_time(
    ctx
    ):
    
    from src.storage import get_user
    user_id = ctx.author.id
    result = get_user(user_id)

    if result:
        time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=result["gmt"])))
        await ctx.respond(embed = discord.Embed(
            title="Time",
            description=f"{time}",
            color=pink
        ))
    else:
        await ctx.respond(embed = discord.Embed(
            title="Error",
            description="You need to register first! Use /register",
            color=pink
        ))


@bot.slash_command(
    name="say_embed",
    description="Repeats the message inside an embed."
)
@discord.option(
    name="nachricht",
    description="Enter the message (e.g., Hello)",
    type=str,
    required=True
)
async def say_embed(
    ctx, 
    nachricht: str = None
    ):

    nachricht = nachricht or ""
    await ctx.respond(embed = discord.Embed(
        title=ctx.author.name+": Says",
        description=nachricht,
        color=purple
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
        color=purple
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
        color=0xc586c0
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
    if user_id == me:
        embed = discord.Embed(
            title="Stop",
            description="Bot stopped.",
            color=grey
        )
        await ctx.respond(embed=embed)
        exit()
    else:
        embed = discord.Embed(
            title="Access denied",
            description="You're not allowed to use this command!",
            color=grey
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
        color=dark_blue
    )
    await ctx.respond(embed=embed)

@bot.slash_command(
    name="palc", 
    description="Palisch Language Converter :3 , Palyischch Lyancuace Convewtew :3"
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
            title="Palisch Cutiee Lyanc :3",
            description=result,
            color=dark_blue
        )
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(result)

async def zar(
    ctx,
    lower_bound: int = None,
    upper_bound: int = None,
    embed: bool = True,
    call=None
    ):
    await ctx.defer()
    if call == "zar_":
        lower_bound = lower_bound or 1
        upper_bound = upper_bound or 20
        from src.random import random_num_generator
        result = random_num_generator(lower_bound, upper_bound)
        if embed == True:
            embed = discord.Embed(
                title="Zar",
                description=result,
                color=dark_blue
            )
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"Zar: {result}")
    else:
        lower_bound = lower_bound or 1
        upper_bound = upper_bound or 1000
        from src.random import random_num_generator
        result = random_num_generator(lower_bound, upper_bound)
        if embed == True:
            embed = discord.Embed(
                title="Random Number",
                description=result,
                color=dark_blue
            )
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"Random Number: {result}")

@bot.slash_command(
    name="zar", 
    description="Generate a random number."
    )
async def zar_(
    ctx,
    lower_bound: int = None,
    upper_bound: int = None,
    embed: bool = True
    ):

    await zar(
        ctx, 
        lower_bound, 
        upper_bound, 
        embed,
        call="zar_"
    )

@bot.slash_command(
    name="random_number", 
    description="Generate a random number."
    )

async def random_number(
    ctx,
    lower_bound: int = None,
    upper_bound: int = None,
    embed: bool = True
    ):
    await zar(
        ctx, 
        lower_bound, 
        upper_bound, 
        embed
    )

@bot.slash_command(
    name="choose", 
    description="Choose a random word from a given text."
    )

async def choose(
    ctx,
    text: str = None,
    embed: bool = True,
    countrys: bool = False,
    names: bool = False
    ):

    if countrys == True:
        text = text or "afghanistan albania algeria andorra angola antigua_and_barbuda argentina armenia australia austria azerbaijan bahamas bahrain bangladesh barbados belarus belgium belize benin bhutan bolivia bosnia_and_herzegovina botswana brazil brunei bulgaria burkina_faso burundi cabo_verde cambodia cameroon canada central_african_republic chad chile china colombia comoros congo costa_rica croatia cuba cyprus czech_republic denmark djibouti dominica dominican_republic ecuador egypt el_salvador equatorial_guinea eritrea estonia swaziland ethiopia fiji finland france gabon gambia georgia germany ghana greece grenada guatemala guinea guinea_bissau guyana haiti honduras hungary iceland india indonesia iran iraq ireland israel italy ivory_coast jamaica japan jordan kazakhstan kenya kiribati kosovo kuwait kyrgyzstan laos latvia lebanon lesotho liberia libya liechtenstein lithuania luxembourg madagascar malawi malaysia maldives mali malta marshall_islands mauritania mauritius mexico micronesia moldova monaco mongolia montenegro morocco mozambique myanmar namibia nauru nepal netherlands new_zealand nicaragua niger nigeria north_korea south_korea north_macedonia norway oman pakistan palau palestine panama papua_new_guinea paraguay peru philippines poland portugal qatar romania russia rwanda saint_kitts_and_nevis saint_lucia saint_vincent_and_the_grenadines samoa san_marino sao_tome_and_principe saudi_arabia senegal serbia seychelles sierra_leone singapore slovakia slovenia solomon_islands somalia south_africa south_sudan spain sri_lanka sudan suriname sweden switzerland syria taiwan tajikistan tanzania thailand timor_leste togo tonga trinidad_and_tobago tunisia turkey turkmenistan tuvalu uganda ukraine united_arab_emirates united_kingdom united_states uruguay uzbekistan vanuatu vatican_city venezuela vietnam yemen zambia zimbabwe"
        await ctx.defer()
        from src.random import choose_word
        result = choose_word(text)
        if embed == True:
            embed = discord.Embed(
                title="Choose a country",
                description=result,
                color=dark_blue
            )
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"Choose a country: {result}")
    elif names == True:
        text = text or "Okyanus Ali james mary john patricia robert jennifer michael linda william elizabeth david barbara richard susan joseph jessica thomas sarah charles karen christopher nancy daniel lisa matthew betty anthony margaret mark sandra donald ashley steven kimberly paul emily andrew donna joshua michelle kenneth carol kevin amanda brian dorothy george melissa edward deborah ronald stephanie timothy rebecca jason sharon jeffrey kathleen ryan amy jacob shirley gary angela nicholas helen eric anna jonathan brenda stephen pamela larry nicole justin samantha scott katherine brandon christine benjamin debra samuel rachel gregory catherine alexander carolyn frank janet raymond heather jack olivia sophia harper owen evelyn amelia lucas grace chloe oliver ava emma isabella charlotte mia lily logan ethan abigail madison ella carter scarlett jayden layla penelope zoey gabriel hudson leo hazel violet aurora savannah brooklyn"
        await ctx.defer()
        from src.random import choose_word
        result = choose_word(text)
        if embed == True:
            embed = discord.Embed(
                title="Choose a name",
                description=result,
                color=dark_blue
            )
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"Choose a name: {result}")
    else:
        text = text or "no_text_given"
        await ctx.defer()
        from src.random import choose_word
        result = choose_word(text)
        if embed == True:
            embed = discord.Embed(
                title="Choose a word",
                description=result,
                color=dark_blue
            )
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"Choose a word: {result}")

@bot.slash_command(
    name="help", 
    description="Provides information about the bot."
    )
async def help(
    ctx
    ):

    embed = discord.Embed(
        title="hello, i'm icelatte :3",
        description="i'm a cute icelatte that brings fun and various tools to your server! if you want to invite me or join my support server, you can use the links below. also, this is an open-source project!",
        color=pink
    )

    embed.add_field(
        name="invite icelatte",
        value="[Click here](https://discord.com/oauth2/authorize?client_id=1505951400281247825&permissions=4503599627373568&integration_type=0&scope=bot)",
        inline=False
    )

    embed.add_field(
        name="main server",
        value="[Click here](https://discord.gg/qsQxHk2V8c)",
        inline=False
    )

    embed.add_field(
        name="gitlab",
        value="[Click here](https://gitlab.com/FluffyPal)",
        inline=True
    )

    embed.add_field(
        name="github",
        value="[Click here](https://github.com/FuffyPal)",
        inline=True
    )

    embed.add_field(
        name="debug",
        value=f"{mode_name} {emoji}",
        inline=True
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
    
bot.run(token)

#power by little-file
#github: https://github.com/little-file/
#II.v

import discord,random

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

u = "QWERTYUIOPASDFGHJKLZXCVBNM"

d = "qazwsxedcrfvtgbyhnujmikol"

s = "!@#$%^&*()_+-=`~[{]}\|;:/?.>,<"

n = "0123456789"

all=u+d+s+n

l = 16

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith("hi"):
        await message.channel.send('Hello')
    
    if message.content.startswith(">>passworld-ganerade"):
        
        p = "".join(random.sample(all,l))

        await message.author.send("your passworld: "+ p)
    if message.content.startswith(">>random-number"):
        
        p = "".join(random.sample(n,l))
        
        await message.channel.send(">>random-number: "+p)
        
    if message.content.startswith(">>random-abcd"):
        
        p = "".join(random.sample(u,d,l))
        
        await message.channel.send("random abcd: "+p)
        
    if message.content.startswith(">>chess.com"):
         await message.channel.send("""        I. https://www.chess.com/analysis/game/computer/47503297?tab=analysis
        II. https://www.chess.com/analysis/game/live/71852224971?tab=review""")
            

    if message.content.startswith(">>author"):
        
        power = "#power by little-file"
        github = "#github: https://github.com/little-file/"
        version = "#II.v"

        await message.channel.send(power+" "+github+" "+version)
        
client.run("your token")

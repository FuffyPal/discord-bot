import discord
from discord import app_commands


def setup_commands(bot, guild_id):
    @bot.tree.command(name="hello", description="Greets the user", guild=guild_id)
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hi {interaction.user.mention}!")

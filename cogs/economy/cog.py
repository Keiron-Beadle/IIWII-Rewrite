import discord
from discord.ext import commands
from discord import app_commands

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='balance', description='Check your balance.')
    async def balance(self, interaction : discord.Interaction):
        return await interaction.response.send_message('Hello World!')
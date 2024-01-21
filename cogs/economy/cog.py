import discord
from discord.ext import commands
from discord import app_commands
import cogs.economy.helpers as helpers

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='balance', description='Check your balance.')
    async def balance(self, interaction : discord.Interaction):
        user_balance = helpers.get_user_balance(interaction.user.id, interaction.guild.id)
        await interaction.response.send_message(f'You have {user_balance.balance} copium.')
import discord
from discord.ext import commands
from discord import app_commands
from cogs.economy import embeds, helpers, views, exceptions

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='balance', description='Check your balance.')
    async def balance(self, interaction : discord.Interaction, currency : str = "Copium"):
        user_balance = helpers.get_user_balance(interaction.user.id, interaction.guild.id)
        amount_of_currency = helpers.get_user_currency(user_balance, currency)
        embed = embeds.make_balance(interaction.user, interaction.guild, amount_of_currency)
        await interaction.response.send_message(view=views.SeeMore(),embed=embed)

    @app_commands.command(name='pay', description='Pay someone.')
    async def pay(self, interaction : discord.Interaction, user : discord.User, amount : int, currency : str = "Copium"):
        try:
            helpers.pay(interaction.user.id, user.id, interaction.guild.id, amount, currency)
        except exceptions.NotEnoughMoney:
            return await interaction.response.send_message('You don\'t have enough money to do that.', ephemeral=True)
        embed = embeds.make_pay(interaction.user, user, amount, interaction.guild, currency)
        await interaction.response.send_message(embed=embed)
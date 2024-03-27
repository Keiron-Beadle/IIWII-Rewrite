import discord
from discord.ext import commands
from discord import app_commands
from cogs.stock import helpers
import cogs.core.helpers as core_helpers
from models.stock import StockMarket

class Stock(commands.GroupCog, name='stock'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='setchannel', description='Set the stock market channel for this server.')
    @app_commands.checks.has_permissions(administrator=True)
    async def setchannel(self, interaction : discord.Interaction, text_channel : discord.TextChannel):
        await helpers.on_set_channel(interaction, text_channel)

    @app_commands.command(name='update', description="Manually request an updated stock chart.")
    @app_commands.commands.check(helpers.guild_has_stock_channel)
    async def update(self, interaction : discord.Interaction):
        await helpers.on_update(interaction)

    @app_commands.command(name='view', description='View a stock.')
    @app_commands.autocomplete(symbol=helpers.stock_list_autocomplete)
    async def view(self, interaction : discord.Interaction, symbol : str):
        await helpers.on_view(interaction, symbol)

    @commands.command(name='stockadd', description='Add a stock to the stock market.')
    async def add(self, ctx, symbol : str, name : str, price : float):
        if not await core_helpers.is_developer(ctx):
            return
        await helpers.on_add_stock(ctx, symbol, name, price)

    @commands.command(name='tick')
    async def tick(self, ctx):
        if not await core_helpers.is_developer(ctx):
            return
        await helpers.on_tick(ctx)

    @commands.command(name='regen')
    async def regen(self, ctx):
        if not await core_helpers.is_developer(ctx):
            return
        await helpers.on_regen(ctx)
import discord
from discord.ext import commands
from discord import app_commands
from cogs.amp import embeds, helpers

class Amp(commands.GroupCog, name='amp'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='servers', description='List all servers that are run by IIWII.')
    async def servers(self, interaction : discord.Interaction):
        await interaction.response.defer()
        servers = await helpers.get_server_list()
        await interaction.followup.send(embed=embeds.server_list(interaction.user, servers))
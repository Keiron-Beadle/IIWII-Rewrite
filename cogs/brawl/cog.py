import discord
from discord.ext import commands
from discord import app_commands
from cogs.brawl import helpers
import database.mariadb as db
from models.brawl import *
from cogs.brawl import embeds

class Brawl(commands.GroupCog, name='brawl'):
    def __init__(self, bot):
        self.bot : discord.Client = bot

    @app_commands.command(name='start', description='Start a new brawl.')
    @app_commands.commands.check(helpers.guild_has_brawl_channel)
    async def start(self, interaction : discord.Interaction, pot : int, image_link : str = None, attachment_image : discord.Attachment = None):
        brawl_channel = self.bot.get_channel(helpers.get_brawl_channel_id(interaction.guild.id))
        await helpers.on_start_brawl(interaction, brawl_channel, pot, image_link, attachment_image)
    
    @app_commands.command(name='setchannel', description='Set the brawl channel for this server.')
    @app_commands.checks.has_permissions(administrator=True)
    async def setchannel(self, interaction : discord.Interaction, text_channel : discord.TextChannel):
        await helpers.on_set_channel(interaction, text_channel)

    @start.error
    async def start_error(self, interaction, error):
        await interaction.response.send_message('No brawl channel set for this server.', ephemeral=True)
        print(error)
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

    @commands.command(name='send_brawl_created')
    async def send_brawl_created(self, ctx):
        request = BrawlRequest(817238795966611466, ctx.author, 100)
        request.set_terms(["hi","helo"])
        request.set_title("Brawl Title")
        await ctx.send(embed=embeds.brawl_created_embed(request))

    @commands.command(name='send_brawl_started')
    async def send_brawl_started(self, ctx):
        request = BrawlRequest(817238795966611466, ctx.author, 100)
        request.set_terms(["hi","helo"])
        request.set_title("Brawl Title")
        response = BrawlResponse(request, ctx.author, ["hi","helo"])
        pre_game = BrawlPreGame(request, response)
        await ctx.send(embed=embeds.brawl_started_embed(pre_game))

    @commands.command(name='send_brawl_cancel_request')
    async def send_brawl_cancel_request(self, ctx):
        request = BrawlRequest(817238795966611466, ctx.author, 100)
        request.set_terms(["hi","helo"])
        request.set_title("Brawl Title")
        await ctx.send(embed=embeds.brawl_request_cancelled_embed(request))

    @commands.command(name='send_pre_game')
    async def send_pre_game(self, ctx):
        request = BrawlRequest(817238795966611466, ctx.author, 100)
        request.set_terms(["hi","helo"])
        request.set_title("Brawl Title")
        response = BrawlResponse(request, ctx.author, ["hi","helo"])
        pre_game = BrawlPreGame(request, response)
        await ctx.send(embed=embeds.brawl_pre_game_embed(pre_game))

    @commands.command(name='send_post_game')
    async def send_post_game(self, ctx):
        request = BrawlRequest(817238795966611466, ctx.author, 100)
        request.set_terms(["hi","helo"])
        request.set_title("Brawl Title")
        response = BrawlResponse(request, ctx.author, ["hi","helo"])
        pre_game = BrawlPreGame(request, response)
        post_game = BrawlPostGame(pre_game, ctx.author)
        await ctx.send(embed=embeds.brawl_post_game_embed(post_game))

    @commands.command(name='send_brawl_cancelled')
    async def send_brawl_cancelled(self, ctx):
        request = BrawlRequest(817238795966611466, ctx.author, 100)
        request.set_terms(["hi","helo"])
        request.set_title("Brawl Title")
        response = BrawlResponse(request, ctx.author, ["hi","helo"])
        pre_game = BrawlPreGame(request, response)
        await ctx.send(embed=embeds.brawl_cancelled_embed(pre_game, ctx.author))

    @start.error
    async def start_error(self, interaction, error):
        await interaction.response.send_message('No brawl channel set for this server.', ephemeral=True)
        print(error)
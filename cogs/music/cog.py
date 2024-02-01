import discord, wavelink
from discord.ext import commands
from discord import app_commands
from cogs.music import helpers

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot : discord.Client = bot

    @app_commands.command(name='play', description='Play a song')
    async def play(self, interaction : discord.Interaction, query : str):
        await helpers.on_play(interaction, query)

    @app_commands.command(name='summon', description='Summon the bot to your voice channel')
    async def summon(self, interaction : discord.Interaction):
        await helpers.on_summon(interaction)

    # Event listeners

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload : wavelink.TrackStartEventPayload):
        requester = self.bot.get_user(payload.track.extras.requester)
        await helpers.on_track_start(payload, requester)

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, payload : wavelink.TrackExceptionEventPayload):
        requester = self.bot.get_user(payload.track.extras.requester)
        await helpers.on_track_exception(payload, requester)

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, payload : wavelink.TrackStuckEventPayload):
        requester = self.bot.get_user(payload.track.extras.requester)
        await helpers.on_track_stuck(payload, requester)

    @commands.Cog.listener()
    async def on_wavelink_inactive_player(player : wavelink.Player):
        guild = player.home
        await helpers.disconnect(player, guild)
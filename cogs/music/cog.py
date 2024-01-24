import discord, wavelink
from discord.ext import commands
from discord import app_commands
from cogs.music import helpers, embeds

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot : discord.Client = bot

    @app_commands.command(name='play', description='Play a song')
    async def play(self, interaction : discord.Interaction, query : str):
        await helpers.on_play(interaction, query)

    # @app_commands.command(name='pause', description='Pause the current song')
    # async def pause(self, interaction : discord.Interaction):
    #     await helpers.on_pause(interaction)

    # @app_commands.command(name='resume', description='Resume the current song')
    # async def resume(self, interaction : discord.Interaction):
    #     await helpers.on_resume(interaction)

    # @app_commands.command(name='skip', description='Skip the current song')
    # async def skip(self, interaction : discord.Interaction):
    #     await helpers.on_skip(interaction)

    # @app_commands.command(name='stop', description='Stop the current song')
    # async def stop(self, interaction : discord.Interaction):
    #     await helpers.on_stop(interaction)

    # @app_commands.command(name='queue', description='Show the current queue')
    # async def queue(self, interaction : discord.Interaction):
    #     await helpers.on_queue(interaction)

    # @app_commands.command(name='loop', description='Loop either the queue or the song.')
    # async def loop(self, interaction: discord.Interaction, loop_type: str = commands.Option(description='Loop type', choices=['queue', 'track'])):
    #     await helpers.on_loop(interaction, loop_type)

    # Event listeners

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload : wavelink.TrackStartEventPayload):
        requester = self.bot.get_user(payload.track.extras['requester'])
        await helpers.on_track_start(payload, requester)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload : wavelink.TrackEndEventPayload):
        requester = self.bot.get_user(payload.track.extras['requester'])
        await helpers.on_track_end(payload, requester)

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, payload : wavelink.TrackExceptionEventPayload):
        requester = self.bot.get_user(payload.track.extras['requester'])
        await helpers.on_track_exception(payload, requester)

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, payload : wavelink.TrackStuckEventPayload):
        requester = self.bot.get_user(payload.track.extras['requester'])
        await helpers.on_track_stuck(payload, requester)

    @commands.Cog.listener()
    async def on_wavelink_inactive_player(player : wavelink.Player):
        await player.disconnect()
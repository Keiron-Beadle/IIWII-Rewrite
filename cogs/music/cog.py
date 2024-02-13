import discord, wavelink
from discord.ext import commands
from discord import app_commands
from cogs.music import helpers

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot : discord.Client = bot

    @app_commands.command(name='setmusicchannel', description='Set the music channel for the server')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setmusicchannel(self, interaction : discord.Interaction, channel : discord.TextChannel):
        await helpers.on_set_music_channel(interaction)

    @app_commands.command(name='play', description='Play a song')
    async def play(self, interaction : discord.Interaction, query : str):
        if not await helpers.get_music_channel(interaction.guild.id):
            return await interaction.response.send_message("Please ask an admin to set the music channel first.", ephemeral=True)
        await helpers.on_play(interaction, query)

    @app_commands.command(name='summon', description='Summon the bot to your voice channel')
    async def summon(self, interaction : discord.Interaction):
        if not await helpers.get_music_channel(interaction.guild.id):
            return await interaction.response.send_message("Please ask an admin to set the music channel first.", ephemeral=True)
        await helpers.on_summon(interaction)

    @app_commands.command(name='addtoplaylist', description='Add a song to a playlist.')
    @app_commands.autocomplete(query=helpers.query_autocomplete)
    async def addtoplaylist(self, interaction : discord.Interaction, query : str):
        await helpers.on_add_to_playlist(interaction, query)

    @app_commands.command(name='removefromplaylist', description='Remove a song from the playlist')
    @app_commands.autocomplete(name=helpers.name_autocomplete)
    async def removefromplaylist(self, interaction : discord.Interaction, name : str):
        await helpers.on_remove_from_playlist(interaction, name)
    
    @app_commands.command(name='updateplaylistdm', description='Update the playlist in your DMs')
    async def updateplaylistdm(self, interaction : discord.Interaction):
        await helpers.on_update_playlist_dm(interaction, self.bot)

    @commands.command(name='checkcache')
    async def checkcache(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        await helpers.check_cache(ctx)

    # Event listeners
        
    @commands.Cog.listener(name='on_voice_state_update')
    async def on_voice_state_update(self, member : discord.Member, before : discord.VoiceState, after : discord.VoiceState):
        await helpers.on_voice_state_update(member, before, after, self.bot)

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
    async def on_wavelink_inactive_player(self, player : wavelink.Player):
        guild = player.home.guild
        await helpers.disconnect(player, guild, self.bot.user)
import discord, wavelink, os
import cogs.music.embeds as embeds
from typing import cast
from dotenv import load_dotenv

load_dotenv()

LAVALINK_HOST = os.getenv('LAVALINK_HOST')
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD')

async def connect_bot_to_voice_channel(interaction : discord.Interaction) -> wavelink.Player:
    if not interaction.guild:
        return
    player : wavelink.Player
    player = cast(wavelink.Player, interaction.guild.voice_client)
    if not player:
        try:
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        except AttributeError:
            raise Exception('You are not in a voice channel.')
        except discord.ClientException:
            raise Exception('Unable to join voice channel.')
        
    if player.channel != interaction.user.voice.channel:
        raise Exception('I am not in your voice channel.')

    player.inactive_timeout = 900
    player.autoplay = wavelink.AutoPlayMode.partial
    return player
    
async def get_tracks(query : str):
    tracks = await wavelink.Playable.search(query, source=wavelink.TrackSource.YouTube)
    if not tracks:
        return None
    return tracks

async def on_play(interaction : discord.Interaction, query : str):
    try:
        player = await connect_bot_to_voice_channel(interaction)        
    except Exception as error:
        return await interaction.response.send_message(error, ephemeral=True)
    
    tracks = await get_tracks(query)
    if not tracks:
        return await interaction.response.send_message('No tracks found.', ephemeral=True)
    
    if isinstance(tracks, wavelink.Playlist):
        for track in tracks.tracks:
            track.extras = {'requester': interaction.user.id}
            await player.queue.put_wait(track)
        return await interaction.response.send_message(f"Added {len(tracks)} tracks to the queue. Starting with {tracks[0].title}.")
    tracks[0].extras = {'requester': interaction.user.id}
    player.queue.put(tracks[0])
    to_play = player.queue.get()
    await player.play(to_play)
    await interaction.response.send_message(f"Added {tracks[0].title} to the queue.")

async def on_track_start(payload : wavelink.TrackStartEventPayload, requester : discord.User):
    embed = embeds.track_started(payload.track, requester)
    await payload.player.channel.send(embed=embed)

async def on_track_end(payload : wavelink.TrackEndEventPayload, requester : discord.User):
    embed = embeds.track_ended(payload.track, requester)
    await payload.player.channel.send(embed=embed)

async def on_track_exception(payload : wavelink.TrackExceptionEventPayload, requester : discord.User):
    embed = embeds.track_exception(payload.track, requester)
    await payload.player.channel.send(embed=embed)
    await payload.player.skip()

async def on_track_stuck(payload : wavelink.TrackStuckEventPayload, requester : discord.User):
    embed = embeds.track_stuck(payload.track, requester)
    await payload.player.channel.send(embed=embed)
    await payload.player.skip()

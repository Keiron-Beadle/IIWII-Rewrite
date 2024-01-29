import discord, wavelink, os, time
from cogs.music import embeds, views, cache
from typing import cast
from dotenv import load_dotenv

load_dotenv()

LAVALINK_HOST = os.getenv('LAVALINK_HOST')
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD')
COMMANDS = {
    "skip" : lambda interaction, original_interaction : on_skip(interaction, original_interaction),
    "loop" : lambda interaction : on_loop(interaction)
}

async def get_player_in_guild(guild : discord.Guild):
    player : wavelink.Player
    player = cast(wavelink.Player, guild.voice_client)
    return player

async def connect_bot_to_voice_channel(interaction : discord.Interaction) -> wavelink.Player:
    if not interaction.guild:
        return
    player = await get_player_in_guild(interaction.guild)
    if not player:
        try:
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
        except AttributeError:
            raise Exception('You are not in a voice channel.')
        except discord.ClientException:
            raise Exception('Unable to join voice channel.')
        
    if player.channel != interaction.user.voice.channel:
        raise Exception('I am not in your voice channel.')

    if not hasattr(player, "home"):
        player.home = interaction.channel
    elif player.home != interaction.channel:
        raise Exception(f'You can only play music in {player.home.mention}.')

    player.inactive_timeout = 900
    player.autoplay = wavelink.AutoPlayMode.partial
    return player
    
async def get_tracks(query : str):
    tracks = await wavelink.Playable.search(query, source=wavelink.TrackSource.YouTube)
    if not tracks:
        return None
    return tracks

async def on_queue(interaction : discord.Interaction):
    player = await get_player_in_guild(interaction.guild)
    if not player:
        return await interaction.response.send_message('Bot likely restarted, needs re-connecting to voice channel.', ephemeral=True)
    embed = embeds.queue(player, player.queue, interaction.user, get_progress_bar=get_progress_bar)
    view = views.QueueView(COMMANDS, interaction, interaction.user)
    await interaction.response.send_message(embed=embed, view=view)

async def on_loop(interaction : discord.Interaction, loop_type : str):
    try:
        player = await connect_bot_to_voice_channel(interaction)
    except Exception as e:
        return await interaction.response.send_message(e, ephemeral=True)
    if loop_type == 'queue':
        player.queue.mode = wavelink.QueueMode.loop_all
    elif loop_type == 'track':
        player.queue.mode = wavelink.QueueMode.loop
    else:
        player.queue.mode = wavelink.QueueMode.normal
    embed = embeds.looped(loop_type, interaction.user)
    await interaction.response.send_message(embed=embed)

async def on_pause(interaction : discord.Interaction):
    try:
        player = await connect_bot_to_voice_channel(interaction)
    except Exception as e:
        return await interaction.response.send_message(e, ephemeral=True)
    await player.pause(True)
    embed = embeds.paused(interaction.user)
    await interaction.response.send_message(embed=embed)

async def on_resume(interaction : discord.Interaction):
    try:
        player = await connect_bot_to_voice_channel(interaction)
    except Exception as e:
        return await interaction.response.send_message(e, ephemeral=True)
    await player.pause(False)
    embed = embeds.unpaused(interaction.user)
    await interaction.response.send_message(embed=embed)

async def on_skip(interaction : discord.Interaction, original_interaction : discord.Interaction):
    player = on_summon(interaction)
    if not player:
        return
    skipped_song = await player.skip()
    if not skipped_song:
        embed = embeds.no_songs_to_skip(interaction.user)   
    else:
        embed = embeds.skipped_song(skipped_song, interaction.user)
    await interaction.response.send_message("Skipped song.", ephemeral=True)
    # original_response = await original_interaction.original_response()
    # if original_response:
    #     thread = await original_response.create_thread(name='Command history')
    #     await thread.send(embed=embed)

async def summon(interaction : discord.Interaction):
    try:
        player = await connect_bot_to_voice_channel(interaction)
    except Exception as e:
        return None


async def on_summon(interaction : discord.Interaction) -> wavelink.Player:
    try:
        player = await connect_bot_to_voice_channel(interaction)
    except Exception as e:
        await interaction.response.send_message(e, ephemeral=True)
        return None
    await interaction.response.send_message(f"Connected to {interaction.user.voice.channel.mention}.", ephemeral=True)
    cache.MUSIC_PANELS[interaction.guild] = await interaction.original_response()
    return player

async def on_play(interaction : discord.Interaction, query : str):
    player = on_summon(interaction)
    if not player:
        return
    tracks = await get_tracks(query)
    if not tracks:
        return await interaction.response.send_message('No tracks found.', ephemeral=True)
    
    if isinstance(tracks, wavelink.Playlist):
        for track in tracks.tracks:
            track.extras = {'requester': interaction.user.id }
            await player.queue.put_wait(track)
            response = f"Added {len(tracks)} tracks to the queue. Starting with {tracks[0].title}."
    else:
        tracks[0].extras = {'requester': interaction.user.id }
        player.queue.put(tracks[0]) 
        response = f"Added {tracks[0].title} to the queue."
    
    if not player.playing:
        await player.play(player.queue.get(), volume=30)
    await interaction.response.send_message(response)

async def on_track_start(payload : wavelink.TrackStartEventPayload, requester : discord.User):
    player : wavelink.Player | None = payload.player
    if not player:
        print("Exception in on_track_start: No player.")
        return
    embed = embeds.track_started(payload.track, requester)
    await player.home.send(embed=embed)

async def on_track_exception(payload : wavelink.TrackExceptionEventPayload, requester : discord.User):
    player : wavelink.Player | None = payload.player
    if not player:
        print("Exception in on_track_exception: No player.")
        return
    embed = embeds.track_exception(payload.track, requester)
    await player.home.send(embed=embed)
    await payload.player.skip()

async def on_track_stuck(payload : wavelink.TrackStuckEventPayload, requester : discord.User):
    player : wavelink.Player | None = payload.player
    if not player:
        print("Exception in on_track_stuck: No player.")
        return
    embed = embeds.track_stuck(payload.track, requester)
    await player.home.send(embed=embed)
    await payload.player.skip()

def get_progress_bar(player : wavelink.Player):
    progress_bar = ''
    track = player.current
    if not track:
        return progress_bar
    total_time = track.length
    current_time = player.position
    progress = current_time / total_time

    number_of_bars = 16
    filled_bars = max(int(progress * number_of_bars), 1)
    progress_bar = '<:BlueLine:1200211417459077171>' * (filled_bars-1)
    progress_bar += '<:MusicMidpoint:1200230385817235571>'
    progress_bar += '<:WhiteLine:1198295966055407727>' * (number_of_bars - filled_bars)
    current_time_str = time.strftime("%M:%S", time.gmtime(current_time * 1e-3))
    total_time_str = time.strftime("%M:%S", time.gmtime(total_time * 1e-3))
    return progress_bar + f'`{current_time_str}/{total_time_str}`'
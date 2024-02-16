import discord, wavelink, os, time, json, re, yt_dlp
from cogs.music import embeds, views, cache, database_queries as queries
from database import mariadb as db
from typing import cast
from dotenv import load_dotenv
from difflib import SequenceMatcher
from discord.ext.commands import Context

load_dotenv()

LAVALINK_HOST = os.getenv('LAVALINK_HOST')
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD')
BOT_REFERENCE : discord.Client = None

COMMANDS = {
    "skip" : lambda interaction : on_skip(interaction),
    "loop" : lambda interaction : on_loop(interaction),
    "update" : lambda interaction : on_update(interaction),
    "shuffle" : lambda interaction : on_shuffle(interaction),
    "disconnect" : lambda interaction : on_disconnect(interaction),
    "send_playlist_dm" : lambda user : send_new_playlist_dm(user, BOT_REFERENCE)
}

def set_bot_reference(bot : discord.Client):
    global BOT_REFERENCE
    BOT_REFERENCE = bot

async def check_cache(context : Context):
    output = ''
    for key,value in cache.USER_VOICE_CHANNELS.items():
        user = context.bot.get_user(key)
        if not user:
            user = await context.bot.fetch_user(key)
        channel = context.bot.get_channel(value)
        if not channel:
            channel = await context.bot.fetch_channel(key)
        if not user or not channel:
            continue
        output += '{'  + f'{user.display_name} : {channel.name} : {channel.guild.name}' + '}\n'
    if len(output) == 0:
        output = 'Nothing in cache.'
    await context.send(output)

async def on_voice_state_update(member : discord.Member, before : discord.VoiceState, after : discord.VoiceState, bot : discord.Client):
    # Update USER_VOICE_CHANNEL cache
    if member.bot and member.id != bot.user.id:
        return
    if after.channel is None:
        if member.id in cache.USER_VOICE_CHANNELS.keys():
            cache.USER_VOICE_CHANNELS.pop(member.id)
    elif after.channel != before.channel or after.channel is not None and before.channel is None:
        if member.id in cache.USER_VOICE_CHANNELS.keys():
            cache.USER_VOICE_CHANNELS[member.id] = after.channel.id
        else:
            cache.USER_VOICE_CHANNELS.update({member.id : after.channel.id})

    # Check for bot empty vc so we can disconnect the bot.
    if before.channel != None:
        for member in before.channel.members:
            if member.id == bot.user.id and len(before.channel.members) == 1:
                player = await get_player_in_guild(member.guild)
                if player:
                    await disconnect(player, member.guild, bot.user)

async def get_player_in_guild(guild : discord.Guild):
    player : wavelink.Player
    player = cast(wavelink.Player, guild.voice_client)
    return player

async def connect_bot_to_voice_channel(interaction : discord.Interaction) -> wavelink.Player:
    return await _connect_bot_to_voice_channel(interaction.guild, interaction.user)

async def _connect_bot_to_voice_channel(guild : discord.Guild, user : discord.User) -> wavelink.Player:
    if not guild:
        return
    channel = await get_music_channel(guild.id)
    player = await get_player_in_guild(guild)
    if not player:
        try:
            player = await user.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
            player.inactive_timeout = 900
            command_history_embed = embeds.dj_hub(player, user, get_progress_bar)
            command_history_view = views.DJHub(COMMANDS, user)
            command_history_message = await channel.send(embed=command_history_embed, view=command_history_view)
            command_history_thread = await command_history_message.create_thread(name='Command history', auto_archive_duration=1440)
            cache.MUSIC_PANELS[guild.id] = command_history_thread
        except AttributeError:
            raise Exception('You are not in a voice channel.')
        except discord.ClientException:
            raise Exception('Unable to join voice channel.')
        
    if player.channel != user.voice.channel:
        raise Exception('I am not in your voice channel.')

    if not hasattr(player, "home"):
        player.home = channel
    elif player.home != channel:
        raise Exception(f'You can only play music in {player.home.mention}.')

    player.inactive_timeout = 900
    player.autoplay = wavelink.AutoPlayMode.partial
    return player
    
async def get_tracks(query : str):
    tracks = await wavelink.Playable.search(query, source=wavelink.TrackSource.YouTube)
    if not tracks:
        return None
    return tracks

async def on_set_music_channel(interaction : discord.Interaction):
    current_music_channel = db.select_one(queries.GET_MUSIC_CHANNEL, (interaction.guild.id,))
    if not current_music_channel:
        db.execute(queries.INSERT_MUSIC_CHANNEL, (interaction.guild.id, interaction.channel.id))
    else:
        db.execute(queries.UPDATE_MUSIC_CHANNEL, (interaction.channel.id, interaction.guild.id))
    cache.MUSIC_CHANNELS[interaction.guild.id] = interaction.channel
    return await interaction.response.send_message(f"Set {interaction.channel.mention} as the music channel.", ephemeral=True)

async def get_music_channel(guild_id : int) -> discord.TextChannel:
    if guild_id in cache.MUSIC_CHANNELS:
        return cache.MUSIC_CHANNELS[guild_id]
    music_channel = db.select_one(queries.GET_MUSIC_CHANNEL, (guild_id,))
    if not music_channel:
        return None
    channel = await BOT_REFERENCE.fetch_channel(music_channel[0])
    cache.MUSIC_CHANNELS[guild_id] = channel
    return channel

async def on_loop(interaction : discord.Interaction):
    try:
        player = await connect_bot_to_voice_channel(interaction)
    except Exception as e:
        return await interaction.response.send_message(e, ephemeral=True)
    if player.queue.mode == wavelink.QueueMode.loop:
        player.queue.mode = wavelink.QueueMode.loop_all
    elif player.queue.mode == wavelink.QueueMode.loop_all:
        player.queue.mode = wavelink.QueueMode.normal
    else:
        player.queue.mode = wavelink.QueueMode.loop
    embed = embeds.looped(player.queue.mode, interaction.user)
    await cache.MUSIC_PANELS[interaction.guild.id].send(embed=embed)
    await update_dj_panel(cache.MUSIC_PANELS[interaction.guild.id], player, interaction.user)
    await interaction.response.send_message("Updated loop mode.", ephemeral=True, delete_after=1)

async def update_dj_panel(thread : discord.Thread, player : wavelink.Player, requester : discord.User):
    embed = embeds.dj_hub(player, requester, get_progress_bar)
    if thread.starter_message:
        if player is None:
            await thread.starter_message.edit(embed=embed,view=None)
        else:
            await thread.starter_message.edit(embed=embed)

async def on_skip(interaction : discord.Interaction):
    player = await summon(interaction)
    if not isinstance(player, wavelink.Player):
        return await interaction.response.send_message("Couldn't find a player in your channel.", ephemeral=True)
    skipped_song = await player.skip()
    if not skipped_song:
        embed = embeds.no_songs_to_skip(interaction.user)   
    else:
        embed = embeds.skipped_song(skipped_song, interaction.user)
    await interaction.response.send_message("Skipped song.", ephemeral=True, delete_after=1)
    await update_dj_panel(cache.MUSIC_PANELS[interaction.guild.id], player, interaction.user)
    await cache.MUSIC_PANELS[interaction.guild.id].send(embed=embed)

async def summon(interaction : discord.Interaction) -> wavelink.Player | Exception:
    try:
        player = await connect_bot_to_voice_channel(interaction)
    except Exception as e:
        return e
    return player

async def on_shuffle(interaction : discord.Interaction):
    player = await summon(interaction)
    if not isinstance(player, wavelink.Player):
        return await interaction.response.send_message(player, ephemeral=True)
    player.queue.shuffle()
    await interaction.response.send_message("Shuffled queue.", ephemeral=True, delete_after=1)
    await update_dj_panel(cache.MUSIC_PANELS[interaction.guild.id], player, interaction.user)

async def on_update(interaction : discord.Interaction):
    player = await summon(interaction)
    if not isinstance(player, wavelink.Player):
        return await interaction.response.send_message(player, ephemeral=True)
    await update_dj_panel(cache.MUSIC_PANELS[interaction.guild.id], player, interaction.user)
    await interaction.response.send_message("Updated command panel.", ephemeral=True, delete_after=1)

async def on_summon(interaction : discord.Interaction):
    player = await summon(interaction)
    if not isinstance(player, wavelink.Player):
        return await interaction.response.send_message(player, ephemeral=True)
    await interaction.response.send_message(f"Connected to {interaction.user.voice.channel.mention}.", ephemeral=True)

async def on_play(interaction : discord.Interaction, query : str):
    player = await summon(interaction)
    if not isinstance(player,wavelink.Player):
        return await interaction.response.send_message(player, ephemeral=True)
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
    await interaction.response.send_message(response, ephemeral=True, delete_after=2)
    await update_dj_panel(cache.MUSIC_PANELS[interaction.guild.id], player, interaction.user)
    await cache.MUSIC_PANELS[interaction.guild.id].send(response)

async def on_add_to_playlist(interaction : discord.Interaction, query : str):
    tracks = await get_tracks(query)
    if not tracks:
        return await interaction.response.send_message('No tracks found.', ephemeral=True)
    if isinstance(tracks, wavelink.Playlist):
        return await interaction.response.send_message('Playlists are not supported.', ephemeral=True)
    playlist_json = db.select_one(queries.GET_USER_PLAYLISTS, (interaction.user.id,))
    if not playlist_json:
        return await interaction.response.send_message("Create a playlist first.", ephemeral=True)
    playlists = json.loads(playlist_json[1])
    view = discord.ui.View(timeout=180)
    select = views.AddToPlaylistSelect(interaction.user.id, playlists, tracks[0], interaction)
    view.add_item(select)
    await interaction.response.send_message(view=view, ephemeral=True)

async def query_autocomplete(interaction : discord.Interaction, current : str):
    tracks = await get_tracks(current)
    if not tracks or len(current) == 0:
        return []
    response = []
    for track in tracks[:10]:
        response.append(discord.app_commands.Choice(name=track.title, value=track.title))
    return response

async def on_disconnect(interaction : discord.Interaction):
    player = await summon(interaction)
    if not isinstance(player, wavelink.Player):
        return await interaction.response.send_message(player, ephemeral=True)
    await disconnect(player, interaction.guild, interaction.user)
    await interaction.response.send_message("Disconnected.", ephemeral=True, delete_after=1)

async def disconnect(player : wavelink.Player, guild : discord.Guild, user : discord.User):
    if player:
        await player.disconnect()
    guild_thread : discord.Thread = cache.MUSIC_PANELS.pop(guild.id, None)
    if not guild_thread:
        return
    try:
        await guild_thread.edit(locked=True,archived=True)
    except discord.Forbidden:
        print(f"Forbidden deletion of thread in: {guild.name}")
    await update_dj_panel(guild_thread, None, user)

async def on_track_start(payload : wavelink.TrackStartEventPayload, requester : discord.User):
    player : wavelink.Player | None = payload.player
    if not player:
        print("Exception in on_track_start: No player.")
        return
    embed = embeds.track_started(payload.track, requester)
    thread = cache.MUSIC_PANELS[player.guild.id]
    await update_dj_panel(thread, payload.player, requester)
    await thread.send(embed=embed)

async def on_track_exception(payload : wavelink.TrackExceptionEventPayload, requester : discord.User):
    player : wavelink.Player | None = payload.player
    if not player:
        print("Exception in on_track_exception: No player.")
        return
    embed = embeds.track_exception(payload.track, requester)
    await cache.MUSIC_PANELS[player.guild.id].send(embed=embed)
    await payload.player.skip()

async def on_track_stuck(payload : wavelink.TrackStuckEventPayload, requester : discord.User):
    player : wavelink.Player | None = payload.player
    if not player:
        print("Exception in on_track_stuck: No player.")
        return
    embed = embeds.track_stuck(payload.track, requester)
    await cache.MUSIC_PANELS[player.guild.id].send(embed=embed)
    await payload.player.skip()

async def on_remove_from_playlist(interaction : discord.Interaction, name : str):
    playlist_json = db.select_one(queries.GET_USER_PLAYLISTS, (interaction.user.id,))
    if not playlist_json:
        return await interaction.response.send_message("Create a playlist first.", ephemeral=True)
    playlists = json.loads(playlist_json[1])
    song_name, playlist_name = name.rsplit(' : ',1)
    for json_playlist_name, tracks in playlists.items():
        if json_playlist_name[:len(playlist_name)] == playlist_name:
            for song in tracks:
                if song['title'][:len(song_name)] == song_name:
                    tracks.remove(song)
                    db.execute(queries.UPDATE_USER_PLAYLISTS, (json.dumps(playlists), interaction.user.id))
                    return await interaction.response.send_message(f"Removed {song_name} from {playlist_name}.", ephemeral=True)
    return await interaction.response.send_message(f"Failed to remove {song_name} from {playlist_name}.", ephemeral=True)

def weighted_ratio(a, b, prefix_length=5, weight_factor=0.75):
    prefix_a = a[:prefix_length]
    prefix_b = b[:prefix_length]
    matcher = SequenceMatcher(None, prefix_a, prefix_b)
    ratio = matcher.quick_ratio()
    weighted_ratio = ratio * (min(len(a), len(b)) / max(len(a), len(b)))
    weighted_ratio *= weight_factor
    
    return weighted_ratio

async def name_autocomplete(interaction : discord.Interaction, current : str):
    playlist_json = db.select_one(queries.GET_USER_PLAYLISTS, (interaction.user.id,))
    if not playlist_json:
        return []
    playlists = json.loads(playlist_json[1])
    response = []
    for playlist_name, tracks in playlists.items():
        highest_song = ''
        highest_song_ratio = -1
        for song in tracks:
            ratio = weighted_ratio(song['title'].lower(), current.lower())
            print(f'{song["title"]} : {current} = {ratio}')
            if ratio > highest_song_ratio:
                highest_song = song['title']
                highest_song_ratio = ratio
        if len(highest_song) > 0:
            playlist_name = playlist_name
            len_playlist = len(playlist_name)
            len_song = len(highest_song)
            if len_playlist > 10:
                playlist_name = playlist_name[:10]
            if len_song + len_playlist > 50:
                highest_song = highest_song[:50-len_playlist]
            choice = f'{highest_song} : {playlist_name}'
            response.append(discord.app_commands.Choice(name=choice, value=choice))
    return response

async def send_new_playlist_dm(user : discord.User, bot : discord.Client) -> bool:
    playlist_json = db.select_one(queries.GET_USER_PLAYLISTS, (user.id,))
    if not playlist_json:
        return False
    playlists = json.loads(playlist_json[1])
    view = discord.ui.View(timeout=None)
    for playlist_name in playlists.keys():
        view.add_item(DynamicPlaylistView(playlist_name, user.id))
    bot.add_view(view)
    dm_channel = user.dm_channel or await user.create_dm()
    async for message in dm_channel.history(limit=None):
        if message.author == bot.user and message.content.startswith('# Your playlists'):
            await message.delete()
            break
    await dm_channel.send('# Your playlists', view=view)
    return True

async def on_update_playlist_dm(interaction : discord.Interaction, bot : discord.Client):
    if not await send_new_playlist_dm(interaction.user, bot):
        return await interaction.response.send_message("Create a playlist first.", ephemeral=True)
    await interaction.response.send_message("Sent to your DMs.", ephemeral=True, delete_after=1)

def get_progress_bar(player : wavelink.Player):
    progress_bar = ''
    if not player:
        return progress_bar
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

class DynamicPlaylistView(discord.ui.DynamicItem[discord.ui.Button],
                      template=r'([\d]*)\u2a0a(.*)',
                      ):

    def __init__(self, playlist : str, user_id):
        self.playlist = playlist
        self.user_id = user_id
        encoded_str = f'{user_id}\u2a0a{playlist}'
        super().__init__(discord.ui.Button(style=discord.ButtonStyle.gray, label=playlist, custom_id=encoded_str))

    @classmethod
    async def from_custom_id(cls, interaction : discord.Interaction, item : discord.ui.Button, match : re.Match[str], /):
        user_id = int(match.group(1))
        playlist = match.group(2)
        return cls(playlist, user_id)
    
    async def callback(self, interaction : discord.Interaction):
        user_voice = None
        user_member : discord.Member = None
        bFoundUser = False
        if interaction.user.id in cache.USER_VOICE_CHANNELS.keys():
            voice_channel = BOT_REFERENCE.get_channel(cache.USER_VOICE_CHANNELS[interaction.user.id])
            if voice_channel:
                for member in voice_channel.members:
                    if member.id == interaction.user.id:
                        user_member = member
                        user_voice = member.voice
                        bFoundUser = True
                        break
        if not bFoundUser:
            for mutual_guild in interaction.user.mutual_guilds:
                for voice_channel in mutual_guild.voice_channels:
                    for member in voice_channel.members:
                        if member.id == interaction.user.id:
                            user_voice = member.voice
                            user_member = member
                            cache.USER_VOICE_CHANNELS.update({interaction.user.id : voice_channel.id})
                            break
                    if user_voice:
                        break
                if user_voice:
                    break

        if not user_voice or user_voice.suppress:
            return await interaction.response.send_message("You need to be in a voice channel, and able to speak to do this.", ephemeral=True)

        if not await get_music_channel(user_member.guild.id):
            return await interaction.response.send_message("Please ask an admin to set the music channel first.", ephemeral=True)

        playlist_json = db.select_one(queries.GET_USER_PLAYLISTS, (self.user_id,))
        if not playlist_json:
            return await interaction.response.send_message("Couldn't get your playlist.", ephemeral=True)
        playlists = json.loads(playlist_json[1])
        track_data = None
        for playlist_name, tracks in playlists.items():
            if playlist_name == self.playlist:
                track_data = tracks
                break

        if not track_data:
            return await interaction.response.send_message(f"Couldn't find any songs in your {self.playlist} playlist.", ephemeral=True)

        try:
            player = await _connect_bot_to_voice_channel(user_member.guild, user_member)
        except Exception as e:
            return await interaction.response.send_message(e, ephemeral=True)
        
        added_song_count = 0
        for song in track_data:
            tracks = await get_tracks(song['uri'])
            if not tracks:
                continue
            
            if isinstance(tracks, wavelink.Playlist):
                for track in tracks.tracks:
                    track.extras = {'requester': interaction.user.id }
                    await player.queue.put_wait(track)
                    added_song_count += 1
            else:
                tracks[0].extras = {'requester': interaction.user.id }
                player.queue.put(tracks[0]) 
                added_song_count += 1

        response = f"Added {added_song_count} tracks to the queue, from {interaction.user.display_name}'s {self.playlist} playlist."    
        if not player.playing:
            await player.play(player.queue.get(), volume=30)
        await interaction.response.send_message(response, ephemeral=True, delete_after=2)
        await update_dj_panel(cache.MUSIC_PANELS[user_member.guild.id], player, user_member)
        await cache.MUSIC_PANELS[user_member.guild.id].send(response)
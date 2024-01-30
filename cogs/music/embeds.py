import time, discord, wavelink
from models.balance import Balance
from discord import Embed, Colour, Member, Guild

COLOURS = {
    'play': Colour.green(),
    'stop': Colour.blue(),
    'pause': Colour.yellow()
}

def track_started(track, requester : discord.User):
    embed = Embed(title=f'Now Playing {track.title}', colour=COLOURS['play'])
    if track.artwork:
        embed.set_thumbnail(url=track.artwork)
    duration_body = f'{time.strftime("%M:%S", time.gmtime(track.length*1e-3))}'
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    embed.add_field(name='Duration', value=duration_body, inline=False)
    embed.set_footer(text=f'Requested by {requester.display_name}')
    return embed

def track_ended(track, requester : discord.User):
    embed = Embed(title=f'Finished Playing {track.title}', colour=COLOURS['stop'])
    if track.artwork:
        embed.set_thumbnail(url=track.artwork)
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    embed.set_footer(text=f'Requested by {requester.display_name}')
    return embed

def track_exception(track, requester : discord.User):
    embed = Embed(title=f'Error playing {track.title}', colour=COLOURS['stop'])
    if track.artwork:
        embed.set_thumbnail(url=track.artwork)
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    embed.set_footer(text=f'Requested by {requester.display_name}')
    return embed

def track_stuck(track, requester : discord.User):
    embed = Embed(title=f'Stuck song detected: {track.title}', colour=COLOURS['stop'])
    if track.artwork:
        embed.set_thumbnail(url=track.artwork)
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    embed.set_footer(text=f'Requested by {requester.display_name}')
    return embed

def paused(requester : discord.User):
    embed = Embed(title=f'Paused', colour=COLOURS['pause'])
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    return embed

def unpaused(requester : discord.User):
    embed = Embed(title=f'Unpaused', colour=COLOURS['play'])
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    return embed

def skipped_song(track, requester : discord.User):
    embed = Embed(title=f'Skipped {track.title}', colour=COLOURS['stop'])
    if track.artwork:
        embed.set_thumbnail(url=track.artwork)
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    return embed

def no_songs_to_skip(requester : discord.User):
    embed = Embed(title=f'No songs to skip', colour=COLOURS['stop'])
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    return embed

def looped(loop_type : wavelink.QueueMode, requester : discord.User):
    if loop_type == wavelink.QueueMode.loop_all:
        title = 'Looped queue'
    elif loop_type == wavelink.QueueMode.loop:
        title = 'Looped current track'
    else:
        title = 'Unlooped the queue.'
    embed = Embed(title=title, colour=COLOURS['play'])
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    return embed

def dj_hub(player : wavelink.Player, queue : wavelink.Queue, requester : discord.User, get_progress_bar : callable):
    embed = Embed(title=f'DJ Hub', colour=COLOURS['play'])
    embed.set_author(name=requester.display_name, icon_url=requester.avatar.url)
    if player and player.current:
        title = (player.current.title[:15] + '...') if len(player.current.title) > 15 else player.current.title
        playing_duration = time.strftime("%M:%S", time.gmtime(player.current.length * 1e-3))
    else:
        title = 'Nothing'
        playing_duration = ''

    length_gap = ((len(title)+1) - len(playing_duration)) // 2
    playing_duration = f"`{' '*length_gap}{playing_duration}{' '*length_gap}`"
    if player and player.current and player.current.uri:
        playing_duration = f'[{playing_duration}]({player.current.uri})'
    embed.add_field(name=f'<:live:1200746819156713472> {title}', value=playing_duration, inline=True)
    
    up_next_title = 'Nothing'
    up_next_duration = ''
    if len(queue) > 0:
        up_next_title = (queue[0].title[:15] + '...') if len(queue[0].title) > 15 else queue[0].title
        up_next_duration = time.strftime("%M:%S", time.gmtime(queue[0].length * 1e-3))
    length_gap = ((len(up_next_title)+1) - len(up_next_duration)) // 2
    up_next_duration = f"`{' '*length_gap}{up_next_duration}{' '*length_gap}`"
    if len(queue) > 0 and queue[0].uri:
        up_next_duration = f'[{up_next_duration}]({queue[0].uri})'
    embed.add_field(name=f'<:next:1200747693086097408> {up_next_title}', value=up_next_duration, inline=True)
    if queue.mode == wavelink.QueueMode.loop:
        loop_state = 'Track'
    elif queue.mode == wavelink.QueueMode.loop_all:
        loop_state = 'Queue'
    else:
        loop_state = 'Nope'
    length_gap = ((len(' Looped?')+2) - len(loop_state)) // 2
    loop_state = f"`{' '*length_gap}{loop_state}{' '*length_gap}`"
    embed.add_field(name='<:loop:1200919712100528209> Looped?', value=loop_state, inline=True)

    song_progress_bar : str = get_progress_bar(player)
    embed.add_field(name=f'\u200b', value=song_progress_bar, inline=False)

    queue_body = ''
    if len(queue) > 1:
        for i in range(1, min(len(queue),5)):
            upcoming_body = f'{queue[i].title[:45]}...' if len(queue[i].title) > 45 else queue[i].title
            queue_body += f'{i}. {upcoming_body}\n'
        embed.add_field(name=f'Upcoming', value=queue_body, inline=False)

    if player and player.current and player.current.artwork:
        embed.set_thumbnail(url=player.current.artwork)
    return embed
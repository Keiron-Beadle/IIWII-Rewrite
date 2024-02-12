import discord

# Maps guild id to a music command history thread.
MUSIC_PANELS : dict[int, discord.Thread] = {}

# Maps guild id to a music channel
MUSIC_CHANNELS : dict[int, discord.TextChannel] = {}

# Maps user id to voice channel id
USER_VOICE_CHANNELS : dict[int, int] = {}
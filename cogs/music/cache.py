import discord

# Maps guild id to a music command history thread.
MUSIC_PANELS : dict[int, discord.Thread] = {}

MUSIC_CHANNELS : dict[int, discord.TextChannel] = {}
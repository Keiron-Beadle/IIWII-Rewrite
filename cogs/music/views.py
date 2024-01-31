import discord, wavelink
import cogs.music.embeds as embeds
import cogs.music.database_queries as queries
from models.playlist import Playlist
import database.mariadb as db
from typing import cast
import json

async def get_player(interaction : discord.Interaction) -> wavelink.Player | None:
    player = cast(wavelink.Player, interaction.guild.voice_client)
    if not player:
        raise Exception("I am not connected to a voice channel.")
    return player

async def is_user_in_vc_as_author(interaction : discord.Interaction, author : discord.User) -> bool:
    if not author.voice:
        await interaction.response.send_message('Original author not in the voice channel anymore, ask for a new /queue.', ephemeral=True)
        return False
    original_author_vc = author.voice.channel
    found_user = False
    for member in original_author_vc.members:
        if member.id == interaction.user.id:
            found_user = True
            break
    if not found_user:
        await interaction.response.send_message("You're not in the voice channel of the author of this queue.", ephemeral=True)
        return False
    return True

# class AddToPlaylistModal(discord.ui.Modal):
#     playlists = discord.ui.Select(placeholder="Select playlist(s)")

#     def __init__(self, author : discord.User, song : wavelink.Playable):
#         title = f"Add {(song.title[:22] + '...') if len(song.title) > 25 else song.title} to playlist(s)"
#         super().__init__(title=title, timeout=180)
#         self.author = author
#         self.song = song
#         playlist_json = db.select_one(queries.GET_USER_PLAYLISTS, (self.author.id,))
#         if playlist_json:
#             playlists = Playlist.json_to_list(playlist_json[1])
#             index = 0
#             for playlist in playlists:
#                 self.playlists.add_option(label=f'{playlist.name} : {len(playlist.tracks)} tracks.', value=index)
#                 index+=1
#         self.playlists.max_values = len(self.playlists.options)

#     async def on_submit(self, interaction : discord.Interaction):
#         if len(self.playlists) == 0:
#             return await interaction.response.send_message("Create a playlist first.", ephemeral=True)
#         playlists_to_add_to = self.playlists.values
#         for to_add in playlists_to_add_to:
#             for playlist in self.playlists:
#                 if playlist.name == to_add.name:
#                     playlist.tracks.append(self.song.uri)
#                     break
#         outputting_json = Playlist.list_to_json(self.playlists)
#         db.execute(queries.UPDATE_USER_PLAYLISTS, (outputting_json, self.author.id))
#         if len(playlists_to_add_to) == 1:
#             await interaction.response.send_message(f"Added {self.song.title} to {playlists_to_add_to[0]}.", ephemeral=True)
#         else:
#             await interaction.response.send_message(f"Added {self.song.title} to {len(playlists_to_add_to)} playlists.", ephemeral=True)

class CreatePlaylistModal(discord.ui.Modal):
    input = discord.ui.TextInput(placeholder="Enter a name", label='Playlist', max_length=25)

    def __init__(self, author : discord.User):
        super().__init__(title=f"Create playlist", timeout=180)
        self.author = author

    async def on_submit(self, interaction : discord.Interaction):
        playlist_json = db.select_one(queries.GET_USER_PLAYLISTS, (self.author.id,))
        if playlist_json:
            playlists = Playlist.json_to_list(playlist_json[1])
            playlists.append(Playlist(name=self.input.value, tracks=[]))
            outputting_json = Playlist.list_to_json(playlists)
            db.execute(queries.UPDATE_USER_PLAYLISTS, (outputting_json, self.author.id))
        else:
            playlists = []
            playlists.append(Playlist(name=self.input.value, tracks=[]))
            outputting_json = Playlist.list_to_json(playlists)
            db.execute(queries.INSERT_USER_PLAYLISTS, (self.author.id, outputting_json))    
        await interaction.response.send_message(f'Created playlist {self.input.value}.', ephemeral=True)

class DJHub(discord.ui.View):
    def __init__(self, commands, original_author):
        super().__init__(timeout=None)
        self.commands = commands
        self.original_author = original_author

    @discord.ui.button(emoji='<:next:1200747693086097408>', style=discord.ButtonStyle.gray)
    async def skip(self, interaction : discord.Interaction, button : discord.ui.Button):
        try:
            await get_player(interaction)
        except Exception as e:
            return await interaction.response.send_message(e, ephemeral=True)
        if not await is_user_in_vc_as_author(interaction, self.original_author):
            return
        await self.commands["skip"](interaction)

    @discord.ui.button(emoji='<:loop:1200919712100528209>', style=discord.ButtonStyle.gray)
    async def loop(self, interaction : discord.Interaction, button : discord.ui.Button):
        try:
            await get_player(interaction)
        except Exception as e:
            return await interaction.response.send_message(e, ephemeral=True)
        if not await is_user_in_vc_as_author(interaction, self.original_author):
            return
        await self.commands["loop"](interaction)

    @discord.ui.button(emoji='<:disconnect:1202363131607924817>', style=discord.ButtonStyle.gray)
    async def disconnect(self, interaction : discord.Interaction, button : discord.ui.Button):
        try:
            await get_player(interaction)
        except Exception as e:
            return await interaction.response.send_message(e, ephemeral=True)
        if not await is_user_in_vc_as_author(interaction, self.original_author):
            return
        await self.commands["disconnect"](interaction)

    @discord.ui.button(emoji='<:shuffle:1202363646215200779>', style=discord.ButtonStyle.gray)
    async def shuffle(self, interaction : discord.Interaction, button : discord.ui.Button):
        try:
            await get_player(interaction)
        except Exception as e:
            return await interaction.response.send_message(e, ephemeral=True)
        if not await is_user_in_vc_as_author(interaction, self.original_author):
            return
        await self.commands["shuffle"](interaction)

    @discord.ui.button(emoji='<:refresh:1201680671777755206>', style=discord.ButtonStyle.gray)
    async def update(self, interaction : discord.Interaction, button : discord.ui.Button):
        try:
            await get_player(interaction)
        except Exception as e:
            return await interaction.response.send_message(e, ephemeral=True)
        if not await is_user_in_vc_as_author(interaction, self.original_author):
            return
        await self.commands["update"](interaction)

    @discord.ui.button(emoji='<:CreatePlaylist:1202375365520130058>', style=discord.ButtonStyle.gray)
    async def create_playlist(self, interaction : discord.Interaction, button : discord.ui.Button):
        modal = CreatePlaylistModal(interaction.user)
        await interaction.response.send_modal(modal)

    @discord.ui.button(emoji='<:AddToPlaylist:1202375364396195880>', style=discord.ButtonStyle.gray)
    async def add_to_playlist(self, interaction : discord.Interaction, button : discord.ui.Button):
        player = await get_player(interaction)
        if not isinstance(player, wavelink.Player):
            return await interaction.response.send_message(player, ephemeral=True)
        if not player.current:
            return await interaction.response.send_message("No song currently playing.", ephemeral=True)
        #modal = AddToPlaylistModal(interaction.user, player.current)
        await interaction.response.send_message("Not implemented yet.", ephemeral=True)
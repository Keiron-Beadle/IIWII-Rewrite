import discord, wavelink
import cogs.music.embeds as embeds
import cogs.music.database_queries as queries
#from models.playlist import Playlist
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

class AddToPlaylistSelect(discord.ui.Select):
    def __init__(self, author_id : int, playlists : dict, song : wavelink.Playable, spawning_interaction : discord.Interaction):
        super().__init__(placeholder="Select playlist(s)")
        self.author_id = author_id
        self.playlists = playlists
        self.spawning_interaction = spawning_interaction
        song_title = song.title[:53] if len(song.title) > 53 else song.title
        self.song = {'title' : song_title, 'uri' : song.uri}
        index = 0
        for key,value in playlists.items():
            self.add_option(label=f'{key} : {len(value)} tracks.', value=index)
            index+=1
        self.max_values = len(self.options)

    async def callback(self, interaction : discord.Interaction):
        for index in self.values:
            index = int(index)
            to_add = self.options[index].label.split(':')[0].strip()
            for key,value in self.playlists.items():
                if key.lower() == to_add.lower():
                    value.append(self.song)
                    break
        outputting_json = json.dumps(self.playlists)
        db.execute(queries.UPDATE_USER_PLAYLISTS, (outputting_json, self.author_id))
        if len(self.values) == 1:
            await interaction.response.send_message(f"Added {self.song['title']} to {self.options[int(self.values[0])].label.split(':')[0].strip()}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Added {self.song['title']} to {len(self.values)} playlists.", ephemeral=True)
        await self.spawning_interaction.delete_original_response()

class CreatePlaylistModal(discord.ui.Modal):
    input = discord.ui.TextInput(placeholder="Enter a name", label='Playlist', max_length=25)

    def __init__(self, author : discord.User):
        super().__init__(title=f"Create playlist", timeout=60)
        self.author = author

    async def on_submit(self, interaction : discord.Interaction):
        playlist_json = db.select_one(queries.GET_USER_PLAYLISTS, (self.author.id,))
        if playlist_json:
            playlists : dict = json.loads(playlist_json[1])
            playlists.update({self.input.value : []})
            outputting_json = json.dumps(playlists)
            db.execute(queries.UPDATE_USER_PLAYLISTS, (outputting_json, self.author.id))
        else:
            playlists = {}
            playlists.update({self.input.value : []})
            outputting_json = json.dumps(playlists)
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
        
        playlist_json = db.select_one(queries.GET_USER_PLAYLISTS, (interaction.user.id,))
        if not playlist_json:
            return await interaction.response.send_message("Create a playlist first.", ephemeral=True)

        playlists = json.loads(playlist_json[1])
        select = AddToPlaylistSelect(interaction.user.id, playlists, player.current, interaction)
        view = discord.ui.View(timeout=60)
        view.add_item(select)

        song_title = (player.current.title[:22] + '...') if len(player.current.title) > 25 else player.current.title
        await interaction.response.send_message(f"Adding {song_title} to your selected playlist(s).", view=view, ephemeral=True)
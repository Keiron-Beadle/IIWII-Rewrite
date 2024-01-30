import discord, wavelink
import cogs.music.embeds as embeds
from typing import cast

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

    @discord.ui.button(emoji='<:refresh:1201680671777755206>', style=discord.ButtonStyle.gray)
    async def update(self, interaction : discord.Interaction, button : discord.ui.Button):
        try:
            await get_player(interaction)
        except Exception as e:
            return await interaction.response.send_message(e, ephemeral=True)
        if not await is_user_in_vc_as_author(interaction, self.original_author):
            return
        await self.commands["update"](interaction)
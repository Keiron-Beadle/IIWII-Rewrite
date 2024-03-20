import discord.ui
import re

class DynamicDeleteButton(discord.ui.DynamicItem[discord.ui.Button],
                            template=r'DeletableMessage([\d]*)',
                            ):
    def __init__(self, message_id=0):
        self.message_id = message_id
        super().__init__(discord.ui.Button(style=discord.ButtonStyle.danger, label='Delete', custom_id=f'DeletableMessage{self.message_id}'))

    @classmethod
    async def from_custom_id(cls, interaction : discord.Interaction, item : discord.ui.Item, match : re.Match[str], /):
        message_id = int(match.group(1))
        return cls(message_id)
        
    async def callback(self, interaction : discord.Interaction):
        message = await interaction.channel.fetch_message(self.message_id)
        await message.delete()
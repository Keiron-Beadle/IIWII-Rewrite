import discord
import cogs.brawl.database_queries as queries
import cogs.brawl.embeds as embeds
import database.mariadb as db
from models.brawl import BrawlRequest

class JoinBrawlButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.success, label='Join')

    async def callback(self, interaction : discord.Interaction):
        db.execute(queries.ADD_BRAWL_PARTICIPANT, (interaction.user.id, self.brawl_id))
        await interaction.response.send_message('You have joined the brawl.', ephemeral=True)

class BrawlRequestModal(discord.ui.Modal):
    title_input = discord.ui.TextInput(label='Brawl Title', placeholder='Title', min_length=1, max_length=50)
    terms_input = discord.ui.TextInput(label='Terms of the Brawl', style=discord.TextStyle.long, placeholder='Each term on a new line!', min_length=1, max_length=800)

    def __init__(self, request : BrawlRequest, brawl_channel : discord.TextChannel):
        super().__init__(title=f'Create Brawl', timeout=300)
        self.request = request
        self.channel = brawl_channel
        
    async def on_submit(self, interaction : discord.Interaction):
        self.request.set_title(self.title_input.value)
        self.request.set_terms(self.terms_input.value.split('\n'))
        db.execute(queries.ADD_BRAWL,(self.request.host.id, self.request.brawl_pot, self.request.title, '\n'.join(self.request.terms), self.request.image))
        await interaction.response.send_message('Brawl created.', ephemeral=True)
        view = discord.ui.View()
        await self.channel.send(embed=embeds.brawl_created_embed(self.request))
        self.stop()
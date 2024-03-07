import discord
import cogs.brawl.database_queries as queries
import cogs.brawl.embeds as embeds
import database.mariadb as db
from models.brawl import BrawlRequest

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
        db.execute(queries.ADD_BRAWL,(self.request.host.id, self.request.brawl_pot, self.request.title, self.request.terms, self.request.image))
        await interaction.response.send_message('Brawl created.', ephemeral=True)
        await self.channel.send(embed=embeds.BrawlCreated(self.request))
        self.stop()
import discord, time
import cogs.brawl.database_queries as queries
import cogs.economy.database_queries as economy_queries
import cogs.brawl.embeds as embeds
import database.mariadb as db
from models.brawl import *

class BrawlStartBrawlView(discord.ui.View):
    def __init__(self, pre_game : BrawlPreGame):
        super().__init__(timeout=None)
        self.pre_game = pre_game

    def set_original_message(self, message : discord.Message):
        self.original_message = message

    @discord.ui.button(label='Start', style=discord.ButtonStyle.green, disabled=True)
    async def start_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        
        await interaction.response.send_message('Brawl started.', ephemeral=True, delete_after=1)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if interaction.user.id != self.pre_game.player1.id and interaction.user.id != self.pre_game.player2.id:
            return await interaction.response.send_message('You cannot cancel this brawl.', ephemeral=True)
        if interaction.user.id == self.pre_game.player1.id:
            # TODO: Delete the brawl from the database
            self.stop()
        elif interaction.user.id == self.pre_game.player2.id:
            # TODO: Reopen the brawl for someone else to join
            self.stop()
        else:
            return await interaction.response.send_message("You cannot cancel this brawl.", ephemeral=True)

class BrawlAcceptView(discord.ui.View):
    def __init__(self, response : BrawlResponse, request_view):
        super().__init__(timeout=None)
        self.response = response
        self.request_view = request_view

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.green)
    async def accept_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        await interaction.response.send_message('Brawl accepted.', ephemeral=True, delete_after=1)
        await self.response.responder.send("Your brawl request has been accepted.", delete_after=30)
        channel = self.response.request.original_message.channel
        await self.response.request.original_message.delete()
        pre_game = BrawlPreGame(self.response.request, self.response)
        pre_game_view = BrawlStartBrawlView()
        pre_game_message = await channel.send(embed=embeds.brawl_pre_game_embed(pre_game), view=pre_game_view)
        pre_game_view.set_original_message(pre_game_message)
        self.stop()

    @discord.ui.button(label='Reject', style=discord.ButtonStyle.red)
    async def reject_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        await interaction.response.send_message('Brawl rejected.', ephemeral=True, delete_after=1)
        await self.response.responder.send("Your brawl request has been rejected.", delete_after=30)
        self.request_view.children[0].disabled = False
        await self.response.request.original_message.edit(embed=self.response.request.original_message.embeds[0], view=self.request_view)
        db.execute(queries.SET_BRAWL_OPPONENT, (0, self.response.request.host.id))
        self.stop()

class BrawlResponseModal(discord.ui.Modal):
    def __init__(self, response : BrawlResponse, request_view):
        super().__init__(title=f'Join Brawl', timeout=300)
        self.response = response
        self.request_view = request_view
        self.terms_input = discord.ui.TextInput(label='Your terms', default='\n'.join(response.request.terms),
                                                placeholder='Modify the terms to your liking, the host will accept/reject them!',
                                                style=discord.TextStyle.long, 
                                                min_length=1, max_length=800)
        self.add_item(self.terms_input)
    
    async def on_timeout(self):
        self.stop()
        self.request_view.children[0].disabled = False
        await self.response.request.original_message.edit(embed=self.response.request.original_message.embeds[0], view=self.request_view)

    async def on_submit(self, interaction : discord.Interaction):
        if self.response.responder.id != interaction.user.id:
            return await interaction.response.send_message('You cannot respond to this brawl.', ephemeral=True)
        self.response.terms = self.terms_input.value.split('\n')
        await interaction.response.send_message('Response submitted.', ephemeral=True)

        view = BrawlAcceptView(self.response, self.request_view)
        await self.response.request.host.send(
            f"{interaction.user.display_name} has responded to your brawl request.\nTerms: {self.terms_input.value}\n\nDo you accept?",
            view=view
            )
        self.stop()

class BrawlRequestView(discord.ui.View):
    def __init__(self, request : BrawlRequest):
        super().__init__(timeout=None)
        self.request = request

    @discord.ui.button(label='Join', style=discord.ButtonStyle.green)
    async def join_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        #if self.request.host.id == interaction.user.id:
        #    return await interaction.response.send_message('You cannot join your own brawl.', ephemeral=True)
        #if db.select_one(queries.GET_USER_ACTIVE_BRAWL, (interaction.user.id, interaction.user.id)):
        #    return await interaction.response.send_message('You are already in a brawl.', ephemeral=True)
        db.execute(queries.SET_BRAWL_OPPONENT, (interaction.user.id, self.request.host.id))
        response = BrawlResponse(self.request, interaction.user, [])
        await interaction.response.send_modal(BrawlResponseModal(response, self))
        self.children[0].disabled = True
        await self.request.original_message.edit(embed=self.request.original_message.embeds[0], view=self)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if interaction.user.id != self.request.host.id:
            return await interaction.response.send_message('You cannot cancel this brawl.', ephemeral=True)
        # TODO: Cancel the brawl and remove from db
        await interaction.response.send_message('Brawl request cancelled.', ephemeral=True, delete_after=1)
        self.stop()

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
        start_time = time.time()
        db.execute(queries.ADD_BRAWL,(self.request.host.id, self.request.title, '\n'.join(self.request.terms), start_time, self.request.brawl_pot, self.request.image))
        await interaction.response.send_message('Brawl created.', ephemeral=True)
        view = BrawlRequestView(self.request)
        msg = await self.channel.send(embed=embeds.brawl_created_embed(self.request), view=view)
        self.request.set_original_message(msg)
        self.stop()
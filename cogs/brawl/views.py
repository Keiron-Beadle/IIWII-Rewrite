import discord, time, json
import cogs.brawl.database_queries as queries
import cogs.economy.database_queries as economy_queries
import cogs.brawl.embeds as embeds
import database.mariadb as db
from models.brawl import *

def get_voters_json(pre_game : BrawlPreGame):
    player1_json = json.dumps(pre_game.player1_pot)
    player2_json = json.dumps(pre_game.player2_pot)
    return f"{{{pre_game.player1.id}:{player1_json},{pre_game.player2.id}:{player2_json}}}"

class BrawlWinnerView(discord.ui.View):
    def __init__(self, pre_game : BrawlPreGame, original_message : discord.Message):
        super().__init__(timeout=None)
        self.pre_game = pre_game
        self.original_message = original_message
        self.winner_according_to_player1 = None
        self.winner_according_to_player2 = None
        self.messages_to_delete = []

    async def check_for_finish(self):
        if not self.winner_according_to_player1 or not self.winner_according_to_player2:
            return
        if self.winner_according_to_player1 != self.winner_according_to_player2:
            to_delete = self.messages_to_delete[:100]
            while len(to_delete) > 0:
                await self.original_message.channel.delete_messages(to_delete)
                self.messages_to_delete = self.messages_to_delete[100:]
                to_delete = self.messages_to_delete[:100]
            await self.original_message.channel.send("The votes are in, but the players have voted for different winners. Agree on a winner to finish the brawl.", delete_after=10)        
            return
        post_game = BrawlPostGame(self.pre_game, self.winner_according_to_player1)
        db.execute(queries.UPDATE_BRAWL_FOR_END, (post_game.winner.id, post_game.game_length, self.pre_game.player1.id))
        # Give money to winner & Give money to voter winners
        await self.original_message.edit(embed=embeds.brawl_post_game_embed(post_game), view=None)

    @discord.ui.button(label='Who won?', style=discord.ButtonStyle.grey, disabled=True)
    async def label_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        pass

    @discord.ui.button(label='Host', style=discord.ButtonStyle.green)
    async def host_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if interaction.user.id == self.pre_game.player1.id:
            self.winner_according_to_player1 = self.pre_game.player1
            msg = await interaction.response.send_message(f"{self.pre_game.player1.display_name} has voted themself as the winner.")
            self.messages_to_delete.append(msg)
            await self.check_for_finish()
            return
        elif interaction.user.id == self.pre_game.player2.id:
            self.winner_according_to_player2 = self.pre_game.player1
            msg = await interaction.response.send_message(f"{self.pre_game.player2.display_name} has voted {self.pre_game.player1.display_name} as the winner.")
            self.messages_to_delete.append(msg)
            await self.check_for_finish()
            return
        return await interaction.response.send_message('You cannot vote on this brawl.', ephemeral=True)

    @discord.ui.button(label='Challenger', style=discord.ButtonStyle.blurple)
    async def challenger_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if interaction.user.id == self.pre_game.player1.id:
            self.winner_according_to_player2 = self.pre_game.player2
            msg = await interaction.response.send_message(f"{self.pre_game.player1.display_name} has voted {self.pre_game.player2.display_name} as the winner.")
            self.messages_to_delete.append(msg)
            await self.check_for_finish()
            return
        elif interaction.user.id == self.pre_game.player2.id:
            self.winner_according_to_player1 = self.pre_game.player2
            msg = await interaction.response.send_message(f"{self.pre_game.player2.display_name} has voted themself as the winner.")
            self.messages_to_delete.append(msg)
            await self.check_for_finish()
            return
        return await interaction.response.send_message('You cannot vote on this brawl.', ephemeral=True)


class BrawlStartBrawlView(discord.ui.View):
    def __init__(self, pre_game : BrawlPreGame):
        super().__init__(timeout=None)
        self.pre_game = pre_game

    def set_original_message(self, message : discord.Message):
        self.original_message = message

    @discord.ui.button(label='Start', style=discord.ButtonStyle.green, disabled=True)
    async def start_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        self.pre_game.start()
        voters_json = get_voters_json(self.pre_game)
        db.execute(queries.UPDATE_BRAWL_FOR_START,
                   (self.pre_game.brawl_pot, voters_json, self.pre_game.start_time))
        await interaction.response.send_message('Brawl started.', ephemeral=True, delete_after=1)
        view = BrawlWinnerView(self.pre_game, self.original_message)
        await self.original_message.edit(embed=embeds.brawl_started_embed(self.pre_game), view=view)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        # If host cancels the game, then cancel it.
        # If the challenger cancels it, then repost it as an open game.
        
        if interaction.user.id == self.pre_game.player1.id:
            db.execute(queries.DELETE_BRAWL, (self.pre_game.player1.id,))
            self.stop()
            await self.original_message.edit(embed=embeds.brawl_cancelled_embed(self.pre_game, self.pre_game.player1), view=None)
            return await interaction.response.send_message('Brawl cancelled.', ephemeral=True, delete_after=1)
        elif interaction.user.id == self.pre_game.player2.id:
            await self.original_message.edit(embed=embeds.brawl_cancelled_embed(self.pre_game, self.pre_game.player2), view=None)
            db.execute(queries.DELETE_BRAWL, (self.pre_game.player1.id,))
            request = BrawlRequest(self.pre_game.player1, self.pre_game.brawl_pot / 2, self.pre_game.image)
            request.set_terms(self.pre_game.original_terms)
            request.set_title(self.pre_game.title)
            view = BrawlRequestView(request)
            msg = await self.original_message.channel.send(embed=embeds.brawl_created_embed(request), view=view)
            view.set_original_message(msg)
            db.execute(queries.ADD_BRAWL,(request.host.id, request.title, '\n'.join(request.terms), request.brawl_pot, request.image))
            self.stop()
            return await interaction.response.send_message('Brawl cancelled.', ephemeral=True, delete_after=1)
        return await interaction.response.send_message("You cannot cancel this brawl.", ephemeral=True)

class BrawlAcceptView(discord.ui.View):
    def __init__(self, response : BrawlResponse, request_view, original_message : discord.Message):
        super().__init__(timeout=None)
        self.response = response
        self.request_view = request_view
        self.original_message = original_message

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.green)
    async def accept_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        await interaction.response.send_message('Brawl accepted.', ephemeral=True, delete_after=1)
        await self.response.responder.send("Your brawl request has been accepted.", delete_after=30)
        channel = self.original_message.channel
        await self.original_message.delete()
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
        await self.response.request.original_message.edit(embed=self.original_message.embeds[0], view=self.request_view)
        db.execute(queries.SET_BRAWL_OPPONENT, (0, self.response.request.host.id))
        self.stop()

class BrawlResponseModal(discord.ui.Modal):
    def __init__(self, response : BrawlResponse, request_view):
        super().__init__(title=f'Join Brawl', timeout=300)
        self.response = response
        self.request_view = request_view
        self.original_message = request_view.original_message
        self.terms_input = discord.ui.TextInput(label='Your terms', default='\n'.join(response.request.terms),
                                                placeholder='Modify the terms to your liking, the host will accept/reject them!',
                                                style=discord.TextStyle.long, 
                                                min_length=1, max_length=800)
        self.add_item(self.terms_input)
    
    async def on_timeout(self):
        self.stop()
        self.request_view.children[0].disabled = False
        await self.original_message.edit(embed=self.original_message.embeds[0], view=self.request_view)

    async def on_submit(self, interaction : discord.Interaction):
        if self.response.responder.id != interaction.user.id:
            return await interaction.response.send_message('You cannot respond to this brawl.', ephemeral=True)
        self.response.terms = self.terms_input.value.split('\n')
        await interaction.response.send_message('Response submitted.', ephemeral=True)

        view = BrawlAcceptView(self.response, self.request_view, self.original_message)
        await self.response.request.host.send(
            f"{interaction.user.display_name} has responded to your brawl request.\nTerms: {self.terms_input.value}\n\nDo you accept?",
            view=view
            )
        self.stop()

class BrawlRequestView(discord.ui.View):
    def __init__(self, request : BrawlRequest):
        super().__init__(timeout=None)
        self.request = request

    def set_original_message(self, message : discord.Message):
        self.original_message = message

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
        await self.original_message.edit(embed=self.original_message.embeds[0], view=self)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if interaction.user.id != self.request.host.id:
            return await interaction.response.send_message('You cannot cancel this brawl.', ephemeral=True)
        db.execute(queries.DELETE_BRAWL, (self.request.host.id,))
        await self.original_message.edit(embed=embeds.brawl_request_cancelled_embed(self.request), view=None)
        await interaction.response.send_message('Brawl cancelled.', ephemeral=True, delete_after=1)
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
        db.execute(queries.ADD_BRAWL,(self.request.host.id, self.request.title, '\n'.join(self.request.terms), self.request.brawl_pot, self.request.image))
        await interaction.response.send_message('Brawl created.', ephemeral=True)
        view = BrawlRequestView(self.request)
        msg = await self.channel.send(embed=embeds.brawl_created_embed(self.request), view=view)
        view.set_original_message(msg)
        self.stop()
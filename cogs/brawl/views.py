import discord, json, asyncio
import cogs.brawl.database_queries as queries
import cogs.economy.database_queries as economy_queries
import cogs.economy.helpers as economy_helpers
import cogs.brawl.embeds as embeds
import database.mariadb as db
from models.brawl import *

MAX_BRAWL_BET = 99
POT_TAX = 0.95

def does_user_have_enough_copium(user_id : int, guild_id : int, amount : int):
    return db.select_one(economy_queries.GET_ECONOMY, (user_id, guild_id))[2] >= amount

def get_voters_json(pre_game : BrawlPreGame):
    player1_json = json.dumps(pre_game.player1_pot)
    player2_json = json.dumps(pre_game.player2_pot)
    return f'''{{"{pre_game.player1.id}":{player1_json},"{pre_game.player2.id}":{player2_json}}}'''

class BrawlWinnerView(discord.ui.View):
    def __init__(self, pre_game : BrawlPreGame, original_message : discord.Message):
        super().__init__(timeout=None)
        self.pre_game = pre_game
        self.original_message = original_message
        self.winner_according_to_player1 = None
        self.winner_according_to_player2 = None
        self.messages_to_delete = []

    async def payout(self):
        post_game = BrawlPostGame(self.pre_game, self.winner_according_to_player1)
        db.execute(queries.UPDATE_BRAWL_FOR_END, (post_game.winner.id, post_game.game_length, self.pre_game.player1.id, self.pre_game.guild.id))
        economy_helpers.admin_pay(post_game.winner.id, self.pre_game.guild.id, post_game.brawl_pot, 'copium')
        loser_pot = sum(post_game.loser_pot.values())
        loser_pot *= POT_TAX
        winner_pot = sum(post_game.winner_pot.values())
        for user_id, user_bet in post_game.winner_pot.items():
            pct = user_bet / winner_pot
            economy_helpers.admin_pay(user_id, self.pre_game.guild.id, pct * loser_pot, 'copium')
        await self.original_message.edit(embed=embeds.brawl_post_game_embed(post_game), view=None)

    async def is_brawl_finished(self):
        if not self.winner_according_to_player1 or not self.winner_according_to_player2:
            return False
        if self.winner_according_to_player1 != self.winner_according_to_player2:
            to_delete = self.messages_to_delete[:100]
            await self.original_message.channel.send("The votes are in, but the players have voted for different winners. Agree on a winner to finish the brawl.", delete_after=7)        
            while len(to_delete) > 0:
                await self.original_message.channel.delete_messages(to_delete)
                self.messages_to_delete = self.messages_to_delete[100:]
                to_delete = self.messages_to_delete[:100]
            self.winner_according_to_player1 = None
            self.winner_according_to_player2 = None
            return False
        return True

    @discord.ui.button(label='Who won?', style=discord.ButtonStyle.grey, disabled=True)
    async def label_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        pass

    @discord.ui.button(label='Host', style=discord.ButtonStyle.green)
    async def host_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if interaction.user.id == self.pre_game.player1.id:
            self.winner_according_to_player1 = self.pre_game.player1
            await interaction.response.send_message(f"{self.pre_game.player1.display_name} has voted themself as the winner.")
        elif interaction.user.id == self.pre_game.player2.id:
            self.winner_according_to_player2 = self.pre_game.player1
            await interaction.response.send_message(f"{self.pre_game.player2.display_name} has voted {self.pre_game.player1.display_name} as the winner.")
        else:
            return await interaction.response.send_message('You cannot vote on this brawl.', ephemeral=True)
        self.messages_to_delete.append(await interaction.original_response())

        if await self.is_brawl_finished():
            await self.payout()

    @discord.ui.button(label='Challenger', style=discord.ButtonStyle.blurple)
    async def challenger_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if interaction.user.id == self.pre_game.player1.id:
            self.winner_according_to_player1 = self.pre_game.player2
            await interaction.response.send_message(f"{self.pre_game.player1.display_name} has voted {self.pre_game.player2.display_name} as the winner.")
        elif interaction.user.id == self.pre_game.player2.id:
            self.winner_according_to_player2 = self.pre_game.player2
            await interaction.response.send_message(f"{self.pre_game.player2.display_name} has voted themself as the winner.")
        else:
            return await interaction.response.send_message('You cannot vote on this brawl.', ephemeral=True)
        self.messages_to_delete.append(await interaction.original_response())

        if await self.is_brawl_finished():
            await self.payout()

class BrawlBetModal(discord.ui.Modal):
    def __init__(self, pre_game : BrawlPreGame, player : discord.User, original_message : discord.Message, view):
        super().__init__(title=f'Bet on {player.display_name}', timeout=30)
        self.pre_game = pre_game
        self.player = player
        self.caller_view = view
        self.original_message = original_message
        self.bet = discord.ui.TextInput(label='Bet', placeholder=f'Amount of Copium: Max {MAX_BRAWL_BET}', min_length=1, max_length=2)
        self.add_item(self.bet)

    async def on_submit(self, interaction: discord.Interaction):
        amount = 0
        try:
            amount = int(self.bet.value)
            if amount < 1:
                raise ValueError()
        except ValueError:
            return await interaction.response.send_message(f'Must be a number between 1-{MAX_BRAWL_BET}.', ephemeral=True)
        original_amount = amount
        
        bet_map = self.pre_game.player1_pot if self.player.id == self.pre_game.player1.id else self.pre_game.player2_pot
    
        if bet_map[interaction.user.id] and bet_map[interaction.user.id] == MAX_BRAWL_BET:
            return await interaction.response.send_message('You have already bet the maximum amount on this brawl.', ephemeral=True)
        if bet_map[interaction.user.id] and bet_map[interaction.user.id] + amount > MAX_BRAWL_BET:
            amount = 99 - bet_map[interaction.user.id]

        if not does_user_have_enough_copium(interaction.user.id, interaction.guild.id, amount):
            return await interaction.response.send_message(f'You do not have enough Copium to bet {original_amount}.', ephemeral=True)
        
        bet_map[interaction.user.id] = bet_map.get(interaction.user.id, 0) + amount
        json = get_voters_json(self.pre_game)
        db.execute(queries.SET_BRAWL_VOTERS, (json, self.pre_game.player1.id))
        
        if original_amount != amount:
            await interaction.response.send_message(f"Modified your bet amount such your total bet doesn't exceed {MAX_BRAWL_BET}. You've bet `{amount}`<:copiumcoin:1117202173147750440>.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You've bet `{amount}`<:copiumcoin:1117202173147750440> on {self.player.display_name}.", ephemeral=True)
        await self.original_message.edit(embed=embeds.brawl_pre_game_embed(self.pre_game), view=self.caller_view)

class BrawlStartBrawlView(discord.ui.View):
    def __init__(self, pre_game : BrawlPreGame):
        super().__init__(timeout=None)
        self.pre_game = pre_game
        self.active_bet_modals : list[BrawlBetModal] = []
        asyncio.create_task(self.enable_start_in_30s())

    def set_original_message(self, message : discord.Message):
        self.original_message = message

    async def enable_start_in_30s(self):
        await asyncio.sleep(30)
        self.children[0].disabled = False
        await self.original_message.edit(embed=embeds.brawl_pre_game_embed(self.pre_game), view=self)

    @discord.ui.button(label='Start', style=discord.ButtonStyle.green, disabled=True)
    async def start_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if interaction.user.id != self.pre_game.player1.id:
            return await interaction.response.send_message("Only the host can start the brawl.", ephemeral=True)
        for modal in self.active_bet_modals:
            await modal.stop()
        self.pre_game.start()
        voters_json = get_voters_json(self.pre_game)
        db.execute(queries.UPDATE_BRAWL_FOR_START,
                   (self.pre_game.brawl_pot, voters_json, self.pre_game.start_time, self.pre_game.player1.id, self.pre_game.guild.id))
        await interaction.response.send_message('Brawl started.', ephemeral=True, delete_after=1)
        view = BrawlWinnerView(self.pre_game, self.original_message)
        await self.original_message.edit(embed=embeds.brawl_started_embed(self.pre_game), view=view)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        # If host cancels the game, then cancel it.
        # If the challenger cancels it, then repost it as an open game.
        guild_id = interaction.guild.id
        if interaction.user.id == self.pre_game.player1.id:
            db.execute(queries.DELETE_BRAWL, (self.pre_game.player1.id,self.pre_game.guild.id))
            economy_helpers.admin_pay(self.pre_game.player1.id, guild_id, self.pre_game.brawl_pot / 2, 'copium')
            self.stop()
            await self.original_message.edit(embed=embeds.brawl_cancelled_embed(self.pre_game, self.pre_game.player1), view=None)
        elif interaction.user.id == self.pre_game.player2.id:
            await self.original_message.edit(embed=embeds.brawl_cancelled_embed(self.pre_game, self.pre_game.player2), view=None)
            db.execute(queries.DELETE_BRAWL, (self.pre_game.player1.id, self.pre_game.guild.id))
            request = BrawlRequest(interaction.guild, self.pre_game.player1, self.pre_game.brawl_pot / 2, self.pre_game.image)
            request.set_terms(self.pre_game.original_terms)
            request.set_title(self.pre_game.title)
            view = BrawlRequestView(request)
            msg = await self.original_message.channel.send(embed=embeds.brawl_created_embed(request), view=view)
            view.set_original_message(msg)
            db.execute(queries.ADD_BRAWL,(request.host.id, request.title, '\n'.join(request.terms), request.brawl_pot, request.image))
            self.stop()
        else:
            return await interaction.response.send_message("You cannot cancel this brawl.", ephemeral=True)

        # Refund all money
        economy_helpers.admin_pay(self.pre_game.player2.id, guild_id, self.pre_game.brawl_pot / 2, 'copium')
        for user_id, user_bet in self.pre_game.player1_pot.values():
            economy_helpers.admin_pay(user_id,guild_id, user_bet, 'copium')
        for user_id, user_bet in self.pre_game.player2_pot.values():
            economy_helpers.admin_pay(user_id,guild_id, user_bet, 'copium')
        await interaction.response.send_message('Brawl cancelled.', ephemeral=True, delete_after=1)
    
    @discord.ui.button(label='Bet:', style=discord.ButtonStyle.gray, disabled=True, row=1)
    async def bet_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        pass

    @discord.ui.button(label='Host', style=discord.ButtonStyle.gray, row=1)
    async def host_bet(self, interaction : discord.Interaction, button : discord.ui.Button):
        #if interaction.user.id == self.pre_game.player1.id or interaction.user.id == self.pre_game.player2.id:
        #    return await interaction.response.send_message("You cannot bet on a brawl you're in!", ephemeral=True)
        #if interaction.user.id in self.pre_game.player1_pot or interaction.user.id in self.pre_game.player2_pot:
        #    return await interaction.response.send_message('You have already bet on this brawl.', ephemeral=True)
        modal = BrawlBetModal(self.pre_game, self.pre_game.player1, self.original_message, self)
        self.active_bet_modals.append(modal)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='Challenger', style=discord.ButtonStyle.gray, row=1)
    async def challenger_bet(self, interaction : discord.Interaction, button : discord.ui.Button):
        #if interaction.user.id == self.pre_game.player1.id or interaction.user.id == self.pre_game.player2.id:
        #    return await interaction.response.send_message("You cannot bet on a brawl you're in!", ephemeral=True)
        #if interaction.user.id in self.pre_game.player1_pot or interaction.user.id in self.pre_game.player2_pot:
        #    return await interaction.response.send_message('You have already bet on this brawl.', ephemeral=True)
        modal = BrawlBetModal(self.pre_game, self.pre_game.player2, self.original_message, self)
        self.active_bet_modals.append(modal)
        await interaction.response.send_modal(modal)
    
class BrawlAcceptView(discord.ui.View):
    def __init__(self, response : BrawlResponse, request_view, original_message : discord.Message):
        super().__init__(timeout=None)
        self.response = response
        self.request_view = request_view
        self.original_message = original_message

    def set_acceptance_message(self, message : discord.Message):
        self.acceptance_message = message

    @discord.ui.button(label='Accept', style=discord.ButtonStyle.green)
    async def accept_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        await self.acceptance_message.delete()
        await interaction.response.send_message('Brawl accepted.', ephemeral=True, delete_after=1)
        await self.response.responder.send("Your brawl request has been accepted.", delete_after=5)
        channel = self.original_message.channel
        await self.original_message.delete()
        pre_game = BrawlPreGame(self.response.request, self.response)
        pre_game_view = BrawlStartBrawlView(pre_game)
        pre_game_message = await channel.send(embed=embeds.brawl_pre_game_embed(pre_game), view=pre_game_view)
        pre_game_view.set_original_message(pre_game_message)
        self.stop()

    @discord.ui.button(label='Reject', style=discord.ButtonStyle.red)
    async def reject_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        await self.acceptance_message.delete()
        await interaction.response.send_message('Brawl rejected.', ephemeral=True, delete_after=1)
        await self.response.responder.send("Your brawl request has been rejected.", delete_after=5)
        self.request_view.children[0].disabled = False
        await self.response.request.original_message.edit(embed=self.original_message.embeds[0], view=self.request_view)
        economy_helpers.admin_pay(self.response.responder.id, interaction.guild.id, self.response.request.brawl_pot, 'copium')
        db.execute(queries.SET_BRAWL_OPPONENT, (0, self.response.request.host.id, self.response.guild.id))
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
        if not does_user_have_enough_copium(interaction.user.id, interaction.guild.id, self.response.request.brawl_pot):
            return await interaction.response.send_message(f'You do not have enough Copium to join this brawl.', ephemeral=True)
        self.response.terms = self.terms_input.value.split('\n')
        await interaction.response.send_message('Response submitted.', ephemeral=True)

        view = BrawlAcceptView(self.response, self.request_view, self.original_message)
        msg = await self.response.request.host.send(
            f"{interaction.user.display_name} has responded to your brawl request.\nTerms:\n{self.terms_input.value}\n\nDo you accept?",
            view=view
            )
        view.set_acceptance_message(msg)
        self.stop()

class BrawlRequestView(discord.ui.View):
    def __init__(self, request : BrawlRequest):
        super().__init__(timeout=None)
        self.request = request
        self.join_modals : list[BrawlResponseModal] = []

    def set_original_message(self, message : discord.Message):
        self.original_message = message

    @discord.ui.button(label='Join', style=discord.ButtonStyle.green)
    async def join_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if self.request.host.id == interaction.user.id:
            return await interaction.response.send_message('You cannot join your own brawl.', ephemeral=True)
        if db.select_one(queries.GET_USER_ACTIVE_BRAWL, (interaction.user.id, interaction.user.id, interaction.guild.id)):
            return await interaction.response.send_message('You are already in a brawl.', ephemeral=True)
        if len(self.join_modals) > 0:
            return await interaction.response.send_message('Someone beat you to it! Try again if the brawl unlocks.', ephemeral=True)
        if not does_user_have_enough_copium(interaction.user.id, interaction.guild.id, self.request.brawl_pot):
            return await interaction.response.send_message(f'You do not have enough Copium to join this brawl.', ephemeral=True)
        economy_helpers.admin_take(interaction.user.id, interaction.guild.id, self.request.brawl_pot, 'copium')
        db.execute(queries.SET_BRAWL_OPPONENT, (interaction.user.id, self.request.host.id, self.request.guild.id))
        response = BrawlResponse(self.request, interaction.user, [])
        join_modal = BrawlResponseModal(response, self)
        self.join_modals.append(join_modal)
        await interaction.response.send_modal(join_modal)
        self.children[0].disabled = True
        await self.original_message.edit(embed=self.original_message.embeds[0], view=self)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction : discord.Interaction, button : discord.ui.Button):
        if interaction.user.id != self.request.host.id:
            return await interaction.response.send_message('You cannot cancel this brawl.', ephemeral=True)
        for modal in self.join_modals:
            modal.stop()
        economy_helpers.admin_pay(self.request.host.id, interaction.guild.id, self.request.brawl_pot, 'copium')
        db.execute(queries.DELETE_BRAWL, (self.request.host.id, self.request.guild.id))
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
        if db.select_one(queries.GET_USER_ACTIVE_BRAWL, (interaction.user.id, interaction.user.id, interaction.guild.id)):
            return await interaction.response.send_message('You are already in a brawl.', ephemeral=True)
        if not does_user_have_enough_copium(interaction.user.id, interaction.guild.id, self.request.brawl_pot):
            return await interaction.response.send_message(f'You do not have enough Copium to start this brawl.', ephemeral=True)
        self.request.set_title(self.title_input.value)
        self.request.set_terms(self.terms_input.value.split('\n'))
        economy_helpers.admin_take(interaction.user.id, interaction.guild.id, self.request.brawl_pot, 'copium')
        db.execute(queries.ADD_BRAWL,(self.request.guild.id, self.request.host.id, self.request.title, '\n'.join(self.request.terms), self.request.brawl_pot, self.request.image))
        await interaction.response.send_message('Brawl created.', ephemeral=True)
        view = BrawlRequestView(self.request)
        msg = await self.channel.send(embed=embeds.brawl_created_embed(self.request), view=view)
        view.set_original_message(msg)
        self.stop()
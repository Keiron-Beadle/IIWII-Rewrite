import discord
import cogs.economy.cache as cache
import cogs.economy.embeds as embeds

class SeeMore(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='More', style=discord.ButtonStyle.blurple)
    async def see_more(self, interaction : discord.Interaction, button : discord.ui.Button):
        balance = cache.get_user_balance(interaction.user.id, interaction.guild.id)
        embed = embeds.make_full_balance(interaction.user, interaction.guild, balance, 0)
        await interaction.response.edit_message(view=SeeLess(balance), embed=embed)
        
class SeeLess(discord.ui.View):
    def __init__(self, balance):
        super().__init__()
        self.start_transaction = 0
        self.page = 1
        self.previous_button = self.children[1]
        self.next_button = self.children[2]
        if self.start_transaction == 0:
            self.previous_button.disabled = True
        if self.start_transaction == len(balance.transactions)-1 or len(balance.transactions) < 10:
            self.next_button.disabled = True

    @discord.ui.button(label='Less', style=discord.ButtonStyle.blurple)
    async def see_less(self, interaction : discord.Interaction, button : discord.ui.Button):
        embed = embeds.make_balance(interaction.user, interaction.guild, cache.get_user_balance(interaction.user.id, interaction.guild.id).copium)
        await interaction.response.edit_message(view=SeeMore(), embed=embed)

    @discord.ui.button(label='<', style=discord.ButtonStyle.gray)
    async def previous(self, interaction : discord.Interaction, button : discord.ui.Button):
        self.start_transaction = max(0, self.start_transaction-10)
        balance = cache.get_user_balance(interaction.user.id, interaction.guild.id)
        embed = embeds.make_full_balance(interaction.user, interaction.guild, balance, self.start_transaction)
        if self.start_transaction == 0:
            button.disabled = True
        if self.start_transaction != len(balance.transactions)-1:
            self.next_button.disabled = False
        await interaction.response.edit_message(view=self, embed=embed)

    @discord.ui.button(label='>', style=discord.ButtonStyle.gray)
    async def next(self, interaction : discord.Interaction, button : discord.ui.Button):
        balance = cache.get_user_balance(interaction.user.id, interaction.guild.id)
        self.start_transaction = min(len(balance.transactions)-1, self.start_transaction+10)
        embed = embeds.make_full_balance(interaction.user, interaction.guild, balance, self.start_transaction)
        if self.start_transaction == len(balance.transactions)-1:
            button.disabled = True
        if self.start_transaction > 0:
            self.previous_button.disabled = False
        await interaction.response.edit_message(view=self, embed=embed)
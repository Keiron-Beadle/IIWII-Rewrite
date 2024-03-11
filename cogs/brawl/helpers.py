import discord
import database.mariadb as db
from cogs.brawl import views
import cogs.brawl.database_queries as queries
import cogs.economy.database_queries as economy_queries
from models.brawl import BrawlRequest

def get_brawl_channel_id(guild_id : int):
    return db.select_one(queries.GET_BRAWL_CHANNEL, (guild_id,))[0]

async def guild_has_brawl_channel(interaction : discord.Interaction):
    brawl_channel_id = get_brawl_channel_id(interaction.guild.id)
    return brawl_channel_id != 0 and interaction.client.get_channel(brawl_channel_id) != None

async def on_start_brawl(interaction : discord.Interaction, brawl_channel_id, pot, image_link, attachment_image):
    if db.select_one(queries.GET_USER_ACTIVE_BRAWL, (interaction.user.id, interaction.user.id, interaction.guild.id)):
        return await interaction.response.send_message('You are already in a brawl.', ephemeral=True)

    user_balance = db.select_one(economy_queries.GET_ECONOMY, (interaction.user.id, interaction.guild.id))[2]
    if user_balance < pot:
        return await interaction.response.send_message(f'You do not have enough Copium to start this brawl.', ephemeral=True)

    if attachment_image:
        image = attachment_image.url
    elif image_link:
        image = image_link
    else:
        image = ''
    request = BrawlRequest(interaction.guild, interaction.user, pot, image)
    modal = views.BrawlRequestModal(request, brawl_channel_id)
    await interaction.response.send_modal(modal)

async def on_set_channel(interaction : discord.Interaction, text_channel : discord.TextChannel):
    db.execute(queries.SET_BRAWL_CHANNEL, (text_channel.id, interaction.guild.id))
    await interaction.response.send_message(f'Brawl channel set to {text_channel.mention}.', ephemeral=True)
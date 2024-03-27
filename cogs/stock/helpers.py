import discord
from database import mariadb as db
import cogs.stock.database_queries as queries
import cogs.core.helpers as core
from models.stock import StockMarket, Stock
import cogs.stock.cache as cache

def get_stock_channel_id(guild_id : int):
    return db.select_one(queries.GET_STOCK_CHANNEL, (guild_id,))[0]

async def guild_has_stock_channel(interaction : discord.Interaction):
    stock_channel_id = get_stock_channel_id(interaction.guild.id)
    return stock_channel_id != 0 and await core.get_channel(interaction.client, stock_channel_id) != None

async def on_set_channel(interaction : discord.Interaction, text_channel : discord.TextChannel):
    db.execute(queries.SET_STOCK_CHANNEL, (text_channel.id, interaction.guild.id))
    await interaction.response.send_message(f'Stock market channel set to {text_channel.mention}.', ephemeral=True)

async def on_update(interaction : discord.Interaction):
    stock_channel_id = get_stock_channel_id(interaction.guild.id)
    try:
        stock_channel = await core.get_channel(interaction.client, stock_channel_id)
    except:
        return await core.send_ephemeral(interaction, 'Stock channel not found. Please set the stock channel with `/stock setchannel`.')
    await core.send(stock_channel, 'Stock update requested.')
    await core.send_ephemeral(interaction, 'Stock update requested.', delete_after=1)

async def on_view(interaction : discord.Interaction, symbol : str):
    stock_market = cache.STOCK_MARKET
    stock = stock_market.get_stock(symbol)
    if not stock:
        return await core.send_ephemeral(interaction, f'Stock {symbol} not found.')
    attachment = discord.File(f'models/stock_images/{symbol}_1day.png')
    await core.send_file(interaction, f'{symbol} - 1 Day', file=attachment)

async def on_add_stock(context, symbol : str, name : str, price : float):
    stock_market = cache.STOCK_MARKET
    stock = Stock(name, symbol, price)
    stock_market.add_stock(stock)
    stock.tick(720)
    price_history = ','.join([str(price) for price in stock.price_history])
    db.execute(queries.ADD_STOCK, (symbol, name, price, price_history, '', stock.volatility))
    await core.send(context, f'Stock {symbol} added.', delete_after=5)

async def on_tick(ctx):
    stock_market = cache.STOCK_MARKET
    stock_market.tick_stock_market()
    await ctx.send('Stock market ticked.')

async def on_regen(ctx):
    stock_market = cache.STOCK_MARKET
    stock_market.regen_images()
    await ctx.send('Stock market regenerated.')

async def stock_list_autocomplete(interaction : discord.Interaction, current : str):
    stock_market = cache.STOCK_MARKET
    response = []
    for stock in stock_market.stocks:
        if stock.symbol.startswith(current) or stock.name.startswith(current) or current.isspace() or len(current) == 0:
            response.append(discord.app_commands.Choice(name=stock.symbol, value=stock.symbol))
    return response
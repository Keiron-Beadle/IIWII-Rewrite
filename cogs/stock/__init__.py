from cogs.stock.cog import Stock

async def setup(bot):
    await bot.add_cog(Stock(bot))
from cogs.brawl.cog import Brawl

async def setup(bot):
    await bot.add_cog(Brawl(bot))
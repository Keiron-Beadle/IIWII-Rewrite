from cogs.core.cog import Core

async def setup(bot):
    await bot.add_cog(Core(bot))
from cogs.amp.cog import Amp

async def setup(bot):
    await bot.add_cog(Amp(bot))
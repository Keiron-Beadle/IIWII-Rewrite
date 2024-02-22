from cogs.jira.cog import Jira

async def setup(bot):
    await bot.add_cog(Jira(bot))
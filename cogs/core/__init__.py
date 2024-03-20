from cogs.core.cog import Core
from cogs.core.views import DynamicDeleteButton

async def setup(bot):
    bot.add_dynamic_items(DynamicDeleteButton)
    await bot.add_cog(Core(bot))
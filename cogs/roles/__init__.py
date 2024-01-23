from cogs.roles.cog import Roles
from cogs.roles.views import DynamicRoleView

async def setup(bot):
    await bot.add_cog(Roles(bot))
    bot.add_dynamic_items(DynamicRoleView)
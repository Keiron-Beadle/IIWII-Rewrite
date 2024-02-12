from cogs.music.cog import Music
from cogs.music import helpers
import wavelink

async def setup(bot):
    helpers.set_bot_reference(bot)
    nodes = [wavelink.Node(uri=helpers.LAVALINK_HOST, password=helpers.LAVALINK_PASSWORD)]
    await wavelink.Pool.connect(nodes=nodes, client=bot, cache_capacity=None)
    await bot.add_cog(Music(bot))
    bot.add_dynamic_items(helpers.DynamicPlaylistView)
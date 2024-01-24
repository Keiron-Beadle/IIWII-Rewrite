from cogs.music.cog import Music
from cogs.music import helpers
import wavelink

async def setup(bot):
    nodes = [wavelink.Node(uri=helpers.LAVALINK_HOST, password=helpers.LAVALINK_PASSWORD)]
    await wavelink.Pool.connect(nodes=nodes, client=bot, cache_capacity=100)
    await bot.add_cog(Music(bot))
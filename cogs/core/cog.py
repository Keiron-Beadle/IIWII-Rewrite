import discord
from discord.ext import commands
from cogs.core.helpers import *

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sync', description='Syncs commands with Discord.')
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx):
        await ctx.message.delete()
        self.bot.tree.copy_global_to(guild=discord.Object(id=ctx.guild.id))
        synced_list = await self.bot.tree.sync(guild=discord.Object(id=ctx.guild.id))
        msg = await send(ctx, f'Synced {len(synced_list)} commands.')
        await msg.delete(delay=5)
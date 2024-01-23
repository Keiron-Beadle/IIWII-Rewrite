import discord
from discord.ext import commands
from discord import app_commands
from cogs.roles import views, helpers

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='makerolemessage', description='Make a message containing the roles of a group in a button menu.')
    async def makerolemessage(self, ctx, group : str):
        await ctx.message.delete()
        roles = helpers.get_roles_of_group(ctx.guild.id, group)
        await helpers.create_roles(ctx, roles)
        await helpers.make_role_messages(ctx, roles, self.bot)

    @commands.command(name='addrole', description='Add a role to the guild.')
    async def addrole(self, ctx, role : str, colour : str, emoji : str, group : str):
        await ctx.message.delete()
        await helpers.add_role(ctx, role, colour, emoji, group)
        msg = await ctx.send(f'Created role {role} with colour {colour} and emoji {emoji}')
        await msg.delete(5)

    @commands.command(name='deleterole', description='Delete a role from the guild.')
    async def deleterole(self, ctx, role : str):
        await ctx.message.delete()
        await helpers.delete_role(ctx, role)
        msg = await ctx.send(f'Deleted role {role}')
        await msg.delete(5)
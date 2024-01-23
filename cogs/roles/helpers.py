from discord.ui import View
from cogs.roles import views
from models.roles import Role
import database.mariadb as db
import cogs.roles.database_queries as queries

def get_roles_of_group(guild_id : int, group : str):
    db_roles = db.select_all(queries.GET_GUILD_ROLES, (guild_id, group))
    ret = []
    if db_roles is None:
        return ret
    for db_role in db_roles:
        ret.append(Role(db_role[0], db_role[1], db_role[2], db_role[3], db_role[4]))
    return ret

def add_role(ctx, role : str, colour : str, emoji : str, group : str):
    db.execute(queries.ADD_GUILD_ROLE, (ctx.guild.id, role, colour, emoji, group))

def delete_role(ctx, role : str):
    db.execute(queries.DELETE_GUILD_ROLE, (ctx.guild.id, role))

async def create_roles(ctx, roles):
    for role in roles:
        bRoleExists = False
        for guild_role in ctx.guild.roles:
            if guild_role.name == role.name:
                bRoleExists = True
                break
        if not bRoleExists:
            await ctx.guild.create_role(reason="IIWII Bot Creating Role", name=role.name, colour=role.colour, mentionable=True)

async def make_role_messages(ctx, roles, bot):
    while len(roles) > 0:
        roles_to_handle = min(len(roles), 25)
        view = View(timeout=None)
        for role in roles[:roles_to_handle]:
            view.add_item(views.DynamicRoleView(role, ctx.guild.id))
        roles = roles[roles_to_handle:]
        await ctx.send('\u2800', view=view)
        bot.add_view(view)
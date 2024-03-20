import discord
import discord.ext.commands as commands
from cogs.core.views import DynamicDeleteButton

async def _send_dm(user : discord.User, content=None, embed=None):
    try:
        msg = await user.send(content=content, embed=embed)
        view = discord.ui.View(timeout=None)
        view.add_item(DynamicDeleteButton(msg.id))
        await msg.edit(content=content, embed=embed, view=view)
    except Exception as e:
        print(e)

async def _send_channel(channel : discord.Interaction, content=None, embed=None, view=None):
    return await channel.send(content=content, embed=embed, view=view)

async def _send_ctx(ctx : commands.Context, content=None, embed=None, view=None):
    return await ctx.send(content=content, embed=embed, view=view)

async def _send_interaction(interaction : discord.Interaction, content=None, embed=None, view=None, ephemeral=False):
    if not view:
        return await interaction.response.send_message(content=content, embed=embed, ephemeral=ephemeral)
    return await interaction.response.send_message(content=content, embed=embed, view=view, ephemeral=ephemeral)

async def send(messageable, content=None):
    try:
        if isinstance(messageable, discord.TextChannel):
            return await _send_channel(messageable, content=content)
        elif isinstance(messageable, discord.Interaction):
            return await _send_interaction(messageable, content=content)
        elif isinstance(messageable, commands.Context):
            return await _send_ctx(messageable, content=content)   
        else:
            return await _send_ctx(messageable, content=content)
    except discord.errors.Forbidden:
        try:
            if isinstance(messageable, discord.TextChannel):
                await _send_dm(messageable.guild.owner, content=f"I don't have permission to send messages in {messageable.mention}. Please make sure I have the `SEND_MESSAGES` permission.")
            elif isinstance(messageable, discord.Interaction):
                await _send_dm(messageable.user, content="I don't have permission to send messages in that channel. Please make sure I have the `SEND_MESSAGES` permission.")
            elif isinstance(messageable, commands.Context):
                await _send_dm(messageable.author, content="I don't have permission to send messages in that channel. Please make sure I have the `SEND_MESSAGES` permission.")
            return None
        except discord.errors.Forbidden:
            return None

async def send_ephemeral(interaction : discord.Interaction, content=None):
    return await _send_interaction(interaction, content=content, ephemeral=True)

async def send_embed(messageable, embed : discord.Embed):
    try:
        if isinstance(messageable, discord.TextChannel):
            return await _send_channel(messageable, embed=embed)
        elif isinstance(messageable, discord.Interaction):
            return await _send_interaction(messageable, embed=embed)
        elif isinstance(messageable, commands.Context):
            return await _send_ctx(messageable, embed=embed)   
        else:
            return await _send_ctx(messageable, embed=embed)
    except discord.errors.Forbidden:
        try:
            if isinstance(messageable, discord.TextChannel):
                await _send_dm(messageable.guild.owner, content=f"I don't have permission to send messages in {messageable.mention}. Please make sure I have the `SEND_MESSAGES` permission.")
            elif isinstance(messageable, discord.Interaction):
                await _send_dm(messageable.user, content="I don't have permission to send messages in that channel. Please make sure I have the `SEND_MESSAGES` permission.")
            elif isinstance(messageable, commands.Context):
                await _send_dm(messageable.author, content="I don't have permission to send messages in that channel. Please make sure I have the `SEND_MESSAGES` permission.")
            return None
        except discord.errors.Forbidden:
            return None

async def send_ephemeral_embed(interaction : discord.Interaction, embed : discord.Embed):
    return await _send_interaction(interaction, embed=embed, ephemeral=True)
        
async def send_embed_view(messageable, embed : discord.Embed, view = discord.ui.View):
    try:
        if isinstance(messageable, discord.TextChannel):
            msg = await _send_channel(messageable, embed=embed, view=view)
            return msg
        elif isinstance(messageable, discord.Interaction):
            msg = await _send_interaction(messageable, embed=embed, view=view)
            return msg
        elif isinstance(messageable, commands.Context):
            msg = await _send_ctx(messageable, embed=embed, view=view)   
            return msg
        else:
            msg = await _send_ctx(messageable, embed=embed, view=view)
            return msg
    except discord.errors.Forbidden:
        try:
            if isinstance(messageable, discord.TextChannel):
                await _send_dm(messageable.guild.owner, content=f"I don't have permission to send messages in {messageable.mention}. Please make sure I have the `SEND_MESSAGES` permission.")
            elif isinstance(messageable, discord.Interaction):
                await _send_dm(messageable.user, content="I don't have permission to send messages in that channel. Please make sure I have the `SEND_MESSAGES` permission.")
            elif isinstance(messageable, commands.Context):
                await _send_dm(messageable.author, content="I don't have permission to send messages in that channel. Please make sure I have the `SEND_MESSAGES` permission.")
            return None
        except discord.errors.Forbidden:
            return None

async def send_ephemeral_embed_view(interaction : discord.Interaction, embed : discord.Embed, view = discord.ui.View):
    return await _send_interaction(interaction, embed=embed, view=view, ephemeral=True)
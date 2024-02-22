import discord
from discord.ext import commands
from discord import app_commands
from cogs.jira import helpers

class Jira(commands.GroupCog, group_name='jira'):
    def __init__(self, bot):
        self.bot : discord.Client = bot

    @app_commands.command(name='all-issues')
    async def all_issues_app(self, interaction : discord.Interaction):
        issues = helpers.get_all_issues()
        await interaction.response.send_message(issues)
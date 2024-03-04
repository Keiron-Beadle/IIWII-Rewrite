import discord
from discord.ext import commands
from discord import app_commands
from cogs.amp import embeds, helpers

class Amp(commands.GroupCog, name='amp'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='servers', description='List all servers that are run by IIWII.')
    @app_commands.guild_only()
    async def servers(self, interaction : discord.Interaction):
        await interaction.response.defer()
        servers = await helpers.get_server_list()
        if servers:
            await interaction.followup.send(embed=embeds.server_list(interaction.user, servers))
        else:
            await interaction.followup.send("Failed to get server list, maybe because login failed.", ephemeral=True)

    @app_commands.command(name='start', description='Start a specified server.')
    @app_commands.guild_only()
    #@app_commands.autocomplete(server=helpers.server_list_autocomplete)
    async def start(self, interaction : discord.Interaction, server : str):
        await interaction.response.defer()
        try:
            await helpers.start_server(server)
            await interaction.followup.send(embed=embeds.server_start(interaction.user, server))
        except Exception as e:
            await interaction.followup.send(embed=embeds.server_start_failed(interaction.user, server, e))

    @app_commands.command(name='stop', description='Stop a specified server.')
    @app_commands.guild_only()
    #@app_commands.autocomplete(server=helpers.server_list_autocomplete)
    async def stop(self, interaction : discord.Interaction, server : str):
        await interaction.response.defer()
        try:
            await helpers.stop_server(server)
            await interaction.followup.send(embed=embeds.server_stop(interaction.user, server))
        except Exception as e:
            await interaction.followup.send(embed=embeds.server_stop_failed(interaction.user, server, e))

    @app_commands.command(name='restart', description='Restart a specified server.')
    @app_commands.guild_only()
    #@app_commands.autocomplete(server=helpers.server_list_autocomplete)
    async def restart(self, interaction : discord.Interaction, server : str):
        await interaction.response.defer()
        try:
            await helpers.restart_server(server)
            await interaction.followup.send(embed=embeds.server_restart(interaction.user, server))
        except Exception as e:
            await interaction.followup.send(embed=embeds.server_restart_failed(interaction.user, server, e))
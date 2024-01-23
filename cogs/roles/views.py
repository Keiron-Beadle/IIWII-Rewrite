import discord, re
from models.roles import Role

class DynamicRoleView(discord.ui.DynamicItem[discord.ui.Button],
                      template=r'([\d]*)\u2a0a(.*)\u2a0a(.*)\u2a0a(.*)\u2a0a(.*)',
                      ):
    def __init__(self, role : Role, guild_id):
        self.role = role
        role_encoding = Role.to_str(role)
        encoded_str = f'{guild_id}\u2a0a{role_encoding}'
        super().__init__(discord.ui.Button(style=discord.ButtonStyle.gray, label=role.name, emoji=role.emoji, custom_id=encoded_str))

    @classmethod
    async def from_custom_id(cls, interaction : discord.Interaction, item : discord.ui.Button, match : re.Match[str], /):
        guild_id = int(match.group(1))
        role = Role(guild_id, match.group(2), match.group(3), match.group(4), match.group(5))
        return cls(role, guild_id)
    
    async def callback(self, interaction : discord.Interaction):
        guild = interaction.guild
        member = guild.get_member(interaction.user.id)
        discord_role = discord.utils.get(guild.roles, name=self.role.name)
        if discord_role in member.roles:
            await member.remove_roles(discord_role)
            await interaction.response.send_message(f"Removed {self.role.name}", ephemeral=True)
        else:
            await member.add_roles(discord_role)
            await interaction.response.send_message(f"Added {self.role.name}", ephemeral=True)
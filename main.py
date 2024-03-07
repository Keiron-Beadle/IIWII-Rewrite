import discord, os
import database.mariadb as db
from cogs import EXTENSIONS
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class IIWIIBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='< ', intents=discord.Intents.all(), application_id=1198446442013003889, case_insensitive=False)

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='her.'))
        print(f"{self.user} finished init.")

    async def setup_hook(self):
        desired_cogs = os.getenv('COGS').split(',')
        desired_cogs = ['cogs.' + cog for cog in desired_cogs]
        for extension in EXTENSIONS:
            if extension in desired_cogs:
                await self.load_extension(extension)

bot = IIWIIBot()

# Ensure a guild config exists for every guild
@bot.before_invoke
async def ensure_guild_config(interaction : discord.Interaction):
    if not interaction.guild:
        return True
    guild_id = interaction.guild.id
    db.execute('''INSERT IGNORE INTO guild_config VALUES (%s)''', (guild_id,))
    return True

bot.run(os.getenv('BOT_TOKEN'))
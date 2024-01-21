import discord, os
from cogs import EXTENSIONS
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class IIWIIBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='< ', intents=discord.Intents.all(), application_id=1198446442013003889, case_insensitive=False)

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='to her.'))
        print(f"{self.user} finished init.")

    async def setup_hook(self):
        desired_cogs = os.getenv('COGS').split(',')
        desired_cogs = ['cogs.' + cog for cog in desired_cogs]
        for extension in EXTENSIONS:
            if extension in desired_cogs:
                await self.load_extension(extension)

bot = IIWIIBot()
bot.run(os.getenv('BOT_TOKEN'))
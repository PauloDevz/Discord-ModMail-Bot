import discord
from discord.ext import commands
from database import Database

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True

class ModMailBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="Hosta",
            intents=intents
        )
        self.db = Database()

    async def setup_hook(self):
        await self.load_extension("cogs.tickets")
        await self.load_extension("cogs.panel")
        await self.tree.sync()

bot = ModMailBot()

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")

bot.run("")
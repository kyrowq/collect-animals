import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class AnimalBot(commands.Bot):
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        #chargement des COGS
        await self.load_extension("cogs.pulls")
        await self.load_extension("cogs.collection")
        await self.load_extension("cogs.quiz")
        await self.load_extension("cogs.description")
        await self.load_extension("cogs.help")
    
bot = AnimalBot()
        
#le bot vient de se connecter
@bot.event
async def on_ready():
    print("------------------------------")
    print(f"Bot connecté : {bot.user}")
    print("collect-animals est opérationnel !")
    print("------------------------------")   

token = os.getenv("DISCORD_TOKEN")

if not token:
    raise ValueError("Tokken Discord introuvable !")
    
bot.run(token)
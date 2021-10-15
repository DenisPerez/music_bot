import discord
from discord.ext import commands

from music_cog import music_cog

bot = commands.Bot(command_prefix='!')

bot.add_cog(music_cog(bot))

@bot.event
async def on_ready():
    print('Kayn is ready to smite the crab.')

token = ""
with open("tokens.txt") as file:
    token = file.read()
    
bot.run(token)
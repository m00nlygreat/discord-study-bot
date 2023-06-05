import os
import discord

from config import TOKEN
from services.dicord_manager import DiscordManager

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = DiscordManager(intents=intents)

print(DISCORD_BOT_TOKEN)
if DISCORD_BOT_TOKEN:
    print('DISCORD_BOT_TOKEN--------------------')
    client.run(DISCORD_BOT_TOKEN)
else:
    print('TOKEN--------------------------------')
    client.run(TOKEN)

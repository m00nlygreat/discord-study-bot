import os
import discord

from config import TOKEN
from services.discord_manager import DiscordManager

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = DiscordManager(intents=intents)

print(DISCORD_BOT_TOKEN)
if DISCORD_BOT_TOKEN:
    print('Use environ [DISCORD_BOT_TOKEN]--------------------')
    client.run(DISCORD_BOT_TOKEN)
else:
    print('Use config [TOKEN]---------------------------------')
    client.run(TOKEN)

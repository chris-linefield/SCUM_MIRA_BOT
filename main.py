import discord
from discord.ext import commands
from config.settings import settings
from controllers.admin_panel_controller import setup_admin_panel
from controllers.registration_controller import setup_registration
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    print(f"Canal principal: {settings.discord_channel_id}")

    await setup_registration(bot, settings.discord_channel_id)
    await setup_admin_panel(bot, settings.discord_channel_id)

bot.run(settings.discord_token)
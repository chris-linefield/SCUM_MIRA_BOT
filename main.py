import discord
from discord.ext import commands
from config import settings
from services.discord_service import DiscordService
from config.constants import CHANNELS
from utils.logger import logger

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    logger.info(f"Bot connecté en tant que {bot.user}")

    await DiscordService.send_registration_panel(bot)

    for merchant_type in CHANNELS.keys():
        await DiscordService.send_shop_panel(bot, merchant_type)

bot.run(settings.discord_token)
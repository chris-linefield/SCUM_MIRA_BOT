import discord
from discord.ext import commands
from discord.ext import tasks
from config import settings
from services.discord_service import DiscordService
from services.scum_manager import ScumManager
from config.constants import CHANNELS
from utils.logger import logger
from datetime import datetime

from views.admin_view import AdminView

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
scum_manager = ScumManager()

@bot.event
async def on_ready():
    logger.info(f"Bot connecté en tant que {bot.user}")
    await DiscordService.send_registration_panel(bot)
    for merchant_type in CHANNELS.keys():
        if merchant_type in ["garage", "armurerie", "moto", "quincaillerie", "restaurateur", "superette"]:
            await DiscordService.send_shop_panel(bot, merchant_type)

    # Envoie le panel administrateur
    admin_channel = bot.get_channel(CHANNELS["admin_panel"])
    if admin_channel:
        await admin_channel.send("🛠 **Panel Administrateur**", view=AdminView())

    # Démarre la tâche de mise à jour de l'embed
    update_status_embed.start()
    # Démarre la tâche de redémarrage automatique de SCUM
    bot.loop.create_task(scum_manager.start_periodic_reboot())

@tasks.loop(minutes=5)
async def update_status_embed():
    status_channel = bot.get_channel(CHANNELS["status"])
    if not status_channel:
        logger.error("Canal de statut introuvable.")
        return

    scum_running = scum_manager.is_scum_running()
    next_reboot = scum_manager.get_next_reboot_time()

    embed = discord.Embed(
        title="📊 **Statut du Bot et de SCUM**",
        color=discord.Color.blue()
    )
    embed.add_field(name="🤖 **Statut du Bot**", value="🟢 En ligne", inline=False)
    embed.add_field(name="🎮 **Statut de SCUM**", value="🟢 En cours d'exécution" if scum_running else "🔴 Hors ligne", inline=False)
    embed.add_field(name="⏱ **Dernière mise à jour**", value=datetime.now().strftime("%H:%M:%S"), inline=False)
    embed.add_field(name="🔄 **Prochain redémarrage**", value=next_reboot.strftime("%H:%M"), inline=False)
    embed.set_footer(text="Mise à jour automatique toutes les 5 minutes.")

    # Met à jour ou envoie l'embed
    messages = [m async for m in status_channel.history(limit=1)]
    if messages:
        await messages[0].edit(embed=embed)
    else:
        await status_channel.send(embed=embed)

bot.run(settings.discord_token)
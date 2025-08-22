import discord
from discord.ext import commands, tasks
from config.settings import settings
from config.constants import CHANNELS, METIER_NAMES, ROLES
from controllers.admin_panel_controller import setup_admin_panel
from controllers.registration_controller import setup_registration
from controllers.garage_panel_controller import setup_garage_console
from controllers.gunsmith_panel_controller import setup_armurerie_console
from controllers.moto_panel_controller import setup_moto_console
from controllers.quincaillerie_panel_controller import setup_quincaillerie_console
from controllers.restaurateur_panel_controller import setup_restaurateur_console
from controllers.storm_controller import setup_storm_panel, storm_status_loop, storm_announce_loop
from controllers.superette_panel_controller import setup_superette_console
import os
import asyncio
import sys
from datetime import datetime, timedelta

from repositories.scum_repository import logger
from services.scum_manager import SCUMManager

# Configuration basique
if not os.path.exists('logs'):
    os.makedirs('logs')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
last_heartbeat = datetime.now()
scum_manager = SCUMManager()

async def purge_channel(channel_id: int):
    """Purge tous les messages du canal spécifié"""
    try:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.purge(limit=100)
            print(f"🧹 Canal {channel_id} purgé avec succès")
        else:
            print(f"❌ Canal {channel_id} introuvable pour la purge")
    except Exception as e:
        print(f"⚠️ Erreur lors de la purge du canal {channel_id}: {e}")

@bot.event
async def on_ready():
    global last_heartbeat
    last_heartbeat = datetime.now()
    print(f"🟢 Bot connecté: {bot.user}")
    print(f"📌 Configuration des panels en cours...")

    # Configuration des panels avec purge (sauf canal admin 1393821678072631346)
    print("🔧 Configuration du panel d'administration...")
    await setup_admin_panel(bot, 1393821678072631346)  # Sans purge

    print("🔧 Configuration du panel d'enregistrement...")
    await purge_channel(1405516212854722691)
    await setup_registration(bot, 1405516212854722691)

    print("🔧 Configuration du panel Garage...")
    await purge_channel(CHANNELS["garage"])
    await setup_garage_console(bot, CHANNELS["garage"])

    print("🔧 Configuration du panel Armurerie...")
    await purge_channel(CHANNELS["armurerie"])
    await setup_armurerie_console(bot, CHANNELS["armurerie"])

    print("🔧 Configuration du panel Moto...")
    await purge_channel(CHANNELS["moto"])
    await setup_moto_console(bot, CHANNELS["moto"])

    print("🔧 Configuration du panel Quincaillerie...")
    await purge_channel(CHANNELS["quincaillerie"])
    await setup_quincaillerie_console(bot, CHANNELS["quincaillerie"])

    print("🔧 Configuration du panel Restaurateur...")
    await purge_channel(CHANNELS["restaurateur"])
    await setup_restaurateur_console(bot, CHANNELS["restaurateur"])

    print("🔧 Configuration du panel Superette...")
    await purge_channel(CHANNELS["superette"])
    await setup_superette_console(bot, CHANNELS["superette"])

    print("✅ Tous les panels ont été configurés avec succès!")
    print("🟢 Bot prêt à l'emploi")

    print("🔧 Configuration du panel Tempêtes...")
    await setup_storm_panel(bot)
    storm_status_loop.start(bot)
    storm_announce_loop.start(bot)

    # Démarrer le service de reboot périodique
    asyncio.create_task(scum_manager.start_periodic_reboot())
    logger.info("⏰ Service de reboot SCUM démarré (5h, 9h, 16h, 21h, 1h)")

@bot.tree.command(name="reboot_scum", description="Redémarre manuellement SCUM")
@commands.has_any_role(*list(ROLES.values()))
async def reboot_scum(interaction: discord.Interaction):
    """Commande pour redémarrer SCUM manuellement"""
    await interaction.response.defer(ephemeral=True)

    success = await scum_manager.reboot_scum()

    if success:
        await interaction.followup.send("✅ SCUM est en cours de redémarrage avec connexion automatique au serveur...", ephemeral=True)
    else:
        await interaction.followup.send("❌ Échec du redémarrage de SCUM", ephemeral=True)


@bot.event
async def on_disconnect():
    """Gère les déconnexions"""
    print("⚠️ Bot déconnecté! Tentative de reconnexion dans 5 secondes...")
    await asyncio.sleep(5)
    try:
        await bot.login(settings.discord_token)
    except Exception as e:
        print(f"❌ Échec de reconnexion: {e}")
        print("🔄 Redémarrage complet du bot...")
        os.execl(sys.executable, sys.executable, *sys.argv)

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Erreur dans {event}: {args}, {kwargs}")
    if event == "on_message":
        channel = bot.get_channel(settings.discord_channel_id)
        if channel:
            try:
                await channel.send("⚠️ Une erreur est survenue. Veuillez réessayer.")
            except:
                pass

try:
    bot.run(settings.discord_token)
except KeyboardInterrupt:
    print("🔴 Arrêt du bot par l'utilisateur")
    sys.exit(0)
except Exception as e:
    print(f"❌ Erreur critique: {e}")
    print("🔄 Redémarrage complet du bot...")
    os.execl(sys.executable, sys.executable, *sys.argv)
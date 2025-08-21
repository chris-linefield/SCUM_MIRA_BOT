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
from controllers.superette_panel_controller import setup_superette_console
import os
import asyncio
import sys
from datetime import datetime, timedelta

from repositories.scum_repository import logger
from services.bot_status_service import BotStatusService
from services.scum_manager import SCUMManager

# Configuration basique
if not os.path.exists('logs'):
    os.makedirs('logs')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
last_heartbeat = datetime.now()
scum_manager = SCUMManager(bot)

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

    asyncio.create_task(scum_manager.start_periodic_check())
    logger.info("⏰ Service de reboot SCUM démarré (5h, 9h, 16h, 21h, 1h)")

    # Démarre les tâches de maintenance
    heartbeat.start()
    connection_check.start()

@tasks.loop(seconds=30)
async def heartbeat():
    """Maintient la connexion active"""
    global last_heartbeat
    last_heartbeat = datetime.now()
    try:
        channel = bot.get_channel(settings.discord_channel_id)
        if channel:
            message = await channel.send("🤖 Ping de maintien")
            await asyncio.sleep(5)
            await message.delete()
    except Exception as e:
        print(f"⚠️ Erreur heartbeat: {e}")
        try:
            await bot.close()
            await bot.login(settings.discord_token)
        except Exception as login_error:
            print(f"❌ Échec de reconnexion après heartbeat: {login_error}")

@tasks.loop(seconds=60)
async def connection_check():
    """Vérifie que la connexion est toujours active"""
    global last_heartbeat
    if (datetime.now() - last_heartbeat) > timedelta(minutes=1):
        print("⚠️ Connexion perdue! Tentative de reconnexion...")
        try:
            await bot.close()
            await bot.login(settings.discord_token)
        except Exception as e:
            print(f"❌ Échec de reconnexion: {e}")

@heartbeat.before_loop
@connection_check.before_loop
async def before_tasks():
    await bot.wait_until_ready()

@bot.tree.command(name="reboot_scum", description="Redémarre manuellement SCUM")
@commands.has_any_role(*list(ROLES.values()))
async def reboot_scum(interaction: discord.Interaction):
    """Commande pour redémarrer SCUM manuellement"""
    await interaction.response.defer(ephemeral=True)

    # Envoyer une annonce avant le reboot manuel
    try:
        success = await scum_manager.send_reboot_announce()
        if success:
            await interaction.followup.send("⚠️ Annonce envoyée ! Redémarrage dans 10 secondes...", ephemeral=True)
            await asyncio.sleep(10)  # Attendre 10 secondes après l'annonce

        success = await scum_manager.reboot_scum()
        if success:
            await interaction.followup.send("✅ SCUM redémarré avec succès !", ephemeral=True)
        else:
            await interaction.followup.send("❌ Échec du redémarrage de SCUM", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Erreur: {str(e)}", ephemeral=True)


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
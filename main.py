import discord
from discord.ext import commands, tasks
from config.settings import settings
from controllers.admin_panel_controller import setup_admin_panel
from controllers.garage_panel_controller import setup_garage_panel
from controllers.registration_controller import setup_registration
import os
import asyncio
import sys
from datetime import datetime, timedelta

if not os.path.exists('logs'):
    os.makedirs('logs')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
last_heartbeat = datetime.now()

@bot.event
async def on_ready():
    global last_heartbeat
    last_heartbeat = datetime.now()
    print(f"🟢 Bot connecté: {bot.user}")
    print(f"📌 Canal principal: {settings.discord_channel_id}")

    await setup_registration(bot, settings.discord_channel_id)
    await setup_admin_panel(bot, settings.discord_channel_id)
    await setup_garage_panel(bot, settings.discord_channel_id)

    heartbeat.start()
    connection_check.start()

@bot.event
async def on_disconnect():
    print("⚠️ Bot déconnecté! Tentative de reconnexion dans 5 secondes...")
    await asyncio.sleep(5)
    try:
        await bot.login(settings.discord_token)
    except Exception as e:
        print(f"❌ Échec de reconnexion: {e}")
        os.execl(sys.executable, sys.executable, *sys.argv)

@tasks.loop(seconds=30)
async def heartbeat():
    global last_heartbeat
    last_heartbeat = datetime.now()

    try:
        channel = bot.get_channel(settings.discord_channel_id)
        if channel:
            message = await channel.send("🤖 Ping de maintien", delete_after=2)
    except Exception as e:
        print(f"⚠️ Erreur heartbeat: {e}")
        await bot.close()
        await bot.login(settings.discord_token)

@tasks.loop(seconds=60)
async def connection_check():
    global last_heartbeat
    if (datetime.now() - last_heartbeat) > timedelta(minutes=1):
        print("⚠️ Connexion perdue! Reconnecting...")
        await bot.close()
        await bot.login(settings.discord_token)

@heartbeat.before_loop
@connection_check.before_loop
async def before_tasks():
    await bot.wait_until_ready()

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Erreur dans {event}: {args}, {kwargs}")
    if event == "on_message":
        channel = bot.get_channel(settings.discord_channel_id)
        if channel:
            await channel.send("⚠️ Une erreur est survenue. Veuillez réessayer.")

try:
    bot.run(settings.discord_token)
except KeyboardInterrupt:
    print("🔴 Arrêt du bot par l'utilisateur")
except Exception as e:
    print(f"❌ Erreur critique: {e}")
    os.execl(sys.executable, sys.executable, *sys.argv)
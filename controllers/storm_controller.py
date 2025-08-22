import asyncio
import discord
from discord.ui import Button, View
from discord.ext import tasks
from datetime import datetime, time, timedelta
from services.scum_manager import SCUMManager
from services.scum_service import send_scum_command
from config.constants import STORM_TIMES, STORM_ANNOUNCE_MESSAGE, STATUS_CHANNEL_ID
from utils.logger import logger

class StormStatusButton(Button):
    def __init__(self):
        super().__init__(
            label="🔄 Actualiser",
            style=discord.ButtonStyle.gray,
            custom_id="storm_status_refresh"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await update_storm_status_message(interaction.client, STATUS_CHANNEL_ID)

class StormAnnounceButton(Button):
    def __init__(self):
        super().__init__(
            label="⚠️ Annonce Tempête (Admin)",
            style=discord.ButtonStyle.red,
            custom_id="storm_announce_manual"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        scum_manager = SCUMManager()
        if not scum_manager.is_scum_running():
            await interaction.followup.send("❌ SCUM n'est pas lancé.", ephemeral=True)
            return
        success, message = await send_scum_command(f"#Announce {STORM_ANNOUNCE_MESSAGE}", interaction.user.id)
        if success:
            await interaction.followup.send("✅ Annonce de tempête envoyée.", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Échec: {message}", ephemeral=True)

async def send_storm_announce(bot):
    """Envoie l'annonce de tempête si SCUM est lancé."""
    scum_manager = SCUMManager()
    if not scum_manager.is_scum_running():
        logger.warning("SCUM n'est pas lancé, annonce de tempête ignorée.")
        return False
    for attempt in range(5):
        success, message = await send_scum_command(f"#Announce {STORM_ANNOUNCE_MESSAGE}", 0)  # 0 = ID système
        if success:
            logger.info("Annonce de tempête envoyée avec succès.")
            return True
        logger.warning(f"Tentative {attempt + 1}/5 échouée: {message}")
        await asyncio.sleep(3)
    logger.error("Échec après 5 tentatives d'envoi de l'annonce de tempête.")
    return False

async def update_storm_status_message(bot, channel_id):
    """Met à jour le message de statut dans le canal spécifié."""
    channel = bot.get_channel(channel_id)
    if not channel:
        logger.error(f"Canal {channel_id} introuvable.")
        return

    # Récupère le dernier message du bot dans le canal
    async for message in channel.history(limit=1):
        if message.author == bot.user:
            embed = message.embeds[0]
            embed.description = (
                f"**Bot en ligne** : {'✅ ON' if bot.is_ready() else '❌ OFF'}\n"
                f"**Dernier ping** : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                f"**Prochaine tempête** : {get_next_storm_time()}"
            )
            await message.edit(embed=embed)
            return

    # Si aucun message existant, en envoie un nouveau
    embed = discord.Embed(
        title="🌪️ **Statut du Bot et Tempêtes**",
        description=(
            f"**Bot en ligne** : {'✅ ON' if bot.is_ready() else '❌ OFF'}\n"
            f"**Dernier ping** : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"**Prochaine tempête** : {get_next_storm_time()}"
        ),
        color=discord.Color.blue()
    )
    view = View(timeout=None)
    view.add_item(StormStatusButton())
    await channel.send(embed=embed, view=view)

def get_next_storm_time():
    """Calcule la prochaine tempête."""
    now = datetime.now()
    today = now.date()
    for storm_time_str in STORM_TIMES:
        storm_time = datetime.strptime(storm_time_str, "%H:%M").time()
        next_storm = datetime.combine(today, storm_time)
        if next_storm > now:
            return next_storm.strftime("%H:%M")
    tomorrow = today + timedelta(days=1)
    next_storm = datetime.combine(tomorrow, datetime.strptime(STORM_TIMES[0], "%H:%M").time())
    return next_storm.strftime("%H:%M")

async def setup_storm_panel(bot):
    """Configure le panel de statut des tempêtes."""
    await update_storm_status_message(bot, STATUS_CHANNEL_ID)

@tasks.loop(minutes=5)
async def storm_status_loop(bot):
    """Met à jour le statut toutes les 5 minutes."""
    await update_storm_status_message(bot, STATUS_CHANNEL_ID)

@tasks.loop(minutes=1)
async def storm_announce_loop(bot):
    """Vérifie et envoie les annonces de tempête."""
    now = datetime.now()
    current_time = now.time()
    for storm_time_str in STORM_TIMES:
        storm_time = datetime.strptime(storm_time_str, "%H:%M").time()
        if current_time.hour == storm_time.hour and current_time.minute == storm_time.minute:
            await send_storm_announce(bot)
            break

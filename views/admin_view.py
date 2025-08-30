import discord
from datetime import datetime, timedelta
from discord.ui import View, Button, Modal, TextInput
from config.constants import ADMIN_ROLES
from services.game_client import GameClient
from services.timer_manager import TimerManager
from utils.logger import logger

class AdminView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RebootSCUMButton())
        self.add_item(RebootBotButton())
        self.add_item(AnnounceButton())
        self.add_item(StartTimerButton())
        self.add_item(CancelTimerButton())

class RebootSCUMButton(Button):
    def __init__(self):
        super().__init__(label="Redémarrer SCUM", style=discord.ButtonStyle.red, custom_id="reboot_scum")

    async def callback(self, interaction: discord.Interaction):
        if not any(role.id in ADMIN_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        from services.scum_manager import ScumManager
        scum_manager = ScumManager()
        success = await scum_manager.reboot_scum()
        if success:
            await interaction.followup.send("✅ SCUM a été redémarré avec succès.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Erreur lors du redémarrage de SCUM.", ephemeral=True)

class RebootBotButton(Button):
    def __init__(self):
        super().__init__(label="Redémarrer le Bot", style=discord.ButtonStyle.red, custom_id="reboot_bot")

    async def callback(self, interaction: discord.Interaction):
        if not any(role.id in ADMIN_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("✅ Le bot va redémarrer dans quelques secondes.", ephemeral=True)
        logger.info(f"Redémarrage du bot demandé par {interaction.user}.")

class AnnounceButton(Button):
    def __init__(self):
        super().__init__(label="Envoyer une annonce", style=discord.ButtonStyle.blurple, custom_id="send_announce")

    async def callback(self, interaction: discord.Interaction):
        if not any(role.id in ADMIN_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        await interaction.response.send_modal(AnnounceModal())

class AnnounceModal(Modal):
    def __init__(self):
        super().__init__(title="Envoyer une annonce personnalisée")
        self.message = TextInput(label="Message", placeholder="Saisissez votre annonce ici...", required=True)
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        message = self.message.value
        success, result_message = await GameClient.announce(message)
        if success:
            logger.info(f"Annonce envoyée par {interaction.user}: {message}")
            await interaction.followup.send(f"✅ Annonce envoyée: {message}", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Erreur lors de l'envoi de l'annonce: {result_message}", ephemeral=True)

# Ajoutez cette classe à admin_view.py
class StartTimerButton(Button):
    def __init__(self):
        super().__init__(label="Démarrer un Timer", style=discord.ButtonStyle.green, custom_id="start_timer")

    async def callback(self, interaction: discord.Interaction):
        if not any(role.id in ADMIN_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return
        await interaction.response.send_modal(TimerModal())

class TimerModal(Modal):
    def __init__(self):
        super().__init__(title="Configurer un Timer")
        self.channel_id = TextInput(
            label="ID du Canal",
            placeholder="Ex: 1407804333281640508",
            required=True
        )
        self.duration = TextInput(
            label="Durée (minutes)",
            placeholder="Ex: 30",
            required=True
        )
        self.event_name = TextInput(
            label="Nom de l'événement",
            placeholder="Ex: Drop d'armes",
            required=True
        )
        self.add_item(self.channel_id)
        self.add_item(self.duration)
        self.add_item(self.event_name)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            channel_id = int(self.channel_id.value)
            duration = int(self.duration.value)
            success = await interaction.client.timer_manager.start_timer(
                interaction.client,  # Passe le bot
                interaction.guild.id,
                channel_id,
                duration,
                self.event_name.value
            )
            if success:
                await interaction.followup.send(
                    f"✅ Timer démarré pour **{self.event_name.value}** dans <#{channel_id}> ({duration} minutes).",
                    ephemeral=True
                )
            else:
                await interaction.followup.send("❌ Erreur lors du démarrage du timer.", ephemeral=True)
        except ValueError:
            await interaction.followup.send("❌ ID de canal ou durée invalide.", ephemeral=True)

class CancelTimerButton(Button):
    def __init__(self):
        super().__init__(label="Annuler un Timer", style=discord.ButtonStyle.red, custom_id="cancel_timer")

    async def callback(self, interaction: discord.Interaction):
        if not any(role.id in ADMIN_ROLES for role in interaction.user.roles):
            await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        await interaction.response.send_modal(CancelTimerModal())

class CancelTimerModal(Modal):
    def __init__(self):
        super().__init__(title="Annuler un Timer")
        self.message_id = TextInput(
            label="ID du Message du Timer",
            placeholder="Ex: 123456789012345678",
            required=True
        )
        self.add_item(self.message_id)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            message_id = int(self.message_id.value)
            timer_manager = interaction.client.timer_manager  # Accès au TimerManager via le bot
            success = await timer_manager.cancel_timer(
                interaction.guild.id,
                interaction.channel.id,
                message_id
            )
            if success:
                await interaction.followup.send(f"✅ Timer annulé.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Timer introuvable.", ephemeral=True)
        except ValueError:
            await interaction.followup.send("❌ ID de message invalide.", ephemeral=True)
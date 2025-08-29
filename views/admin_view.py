# admin_view.py
import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from config.constants import ADMIN_ROLES
from services.game_client import GameClient
from utils.logger import logger

class AdminView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RebootSCUMButton())
        self.add_item(RebootBotButton())
        self.add_item(AnnounceButton())

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
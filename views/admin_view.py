import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from config.constants import ADMIN_ROLES
from services.scum_manager import ScumManager
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
        # Pour redémarrer le bot, vous pouvez utiliser `os.execv` ou un système externe.
        # Exemple basique (à adapter selon votre hébergement) :
        # import os
        # os.execv(__file__, ['python'] + sys.argv)

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
        # Logique pour envoyer l'annonce dans le jeu ou un canal Discord
        logger.info(f"Annonce envoyée par {interaction.user}: {self.message.value}")
        await interaction.followup.send(f"✅ Annonce envoyée: {self.message.value}", ephemeral=True)
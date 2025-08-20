# controllers/admin_panel_controller.py
import discord
from discord.ui import Button, View
from discord import Interaction

from config.constants import ROLES
from services.scum_manager import SCUMManager
from utils.action_logger import ActionLogger

class AdminRebootButton(Button):
    def __init__(self):
        super().__init__(
            label="🔄 Redémarrer SCUM",
            style=discord.ButtonStyle.danger,
            custom_id="admin_reboot_scum"
        )
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            # Vérification du rôle admin
            if not any(role.id in ROLES.values() for role in interaction.user.roles):
                await interaction.followup.send("❌ Rôle administrateur requis.", ephemeral=True)
                return

            scum_manager = SCUMManager()
            success = await scum_manager.reboot_scum()

            if success:
                await interaction.followup.send("✅ SCUM est en cours de redémarrage...", ephemeral=True)
                self.logger.log_action(
                    interaction.user.id,
                    "admin_reboot_scum",
                    "manual",
                    "success",
                    "Redémarrage manuel de SCUM"
                )
            else:
                await interaction.followup.send("❌ Échec du redémarrage de SCUM", ephemeral=True)
                self.logger.log_action(
                    interaction.user.id,
                    "admin_reboot_scum",
                    "manual",
                    "failed",
                    "Échec du redémarrage manuel de SCUM"
                )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)
            self.logger.log_action(
                interaction.user.id,
                "admin_reboot_scum",
                "manual",
                "error",
                str(e)
            )
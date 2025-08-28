import discord
from discord.ui import Button, View
from discord import Interaction
from controllers.storm_controller import StormAnnounceButton
from services.scum_manager import SCUMManager
from services.bank_service import BankService
from utils.action_logger import ActionLogger
from config.constants import ROLES

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

class TopBalanceButton(Button):
    def __init__(self):
        super().__init__(
            label="🏆 Top 5 des soldes",
            style=discord.ButtonStyle.secondary,
            custom_id="top_bank_balance"
        )
        self.bank_service = BankService()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            if not any(role.id in ROLES.values() for role in interaction.user.roles):
                await interaction.followup.send("❌ Rôle administrateur requis.", ephemeral=True)
                return

            top_balances, message = await self.bank_service.get_top_balances()
            if not top_balances:
                await interaction.followup.send(f"❌ **Erreur** : {message}", ephemeral=True)
                return

            embed = discord.Embed(
                title="🏆 **Top 5 des soldes bancaires**",
                color=discord.Color.gold()
            )
            for i, (name, balance) in enumerate(top_balances, start=1):
                embed.add_field(name=f"#{i} - {name}", value=f"**{balance}** crédits", inline=False)

            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur TopBalanceButton: {e}")
            await interaction.followup.send("❌ **Erreur critique** : Impossible de récupérer les soldes.", ephemeral=True)

def send_admin_panel_message():
    """Crée le message et la vue pour le panel d'administration"""
    embed = discord.Embed(
        title="🛠️ **Panel Administration - M.I.R.A**",
        description=(
            "*Un terminal s'allume devant vous, affichant les options disponibles.*\n\n"
            "**🔹 Actions disponibles :**\n"
            "- Redémarrer SCUM\n"
            "- Annonce Tempête (Admin)\n"
            "- Top 5 des soldes bancaires"
        ),
        color=discord.Color.dark_blue()
    )
    view = View(timeout=None)
    view.add_item(AdminRebootButton())
    view.add_item(StormAnnounceButton())
    view.add_item(TopBalanceButton())
    return embed, view

async def setup_admin_panel(bot, channel_id: int):
    """Envoie le panel d'administration dans le canal spécifié"""
    channel = bot.get_channel(channel_id)
    if channel:
        embed, view = send_admin_panel_message()
        await channel.send(embed=embed, view=view)
    else:
        print(f"❌ Canal {channel_id} introuvable.")

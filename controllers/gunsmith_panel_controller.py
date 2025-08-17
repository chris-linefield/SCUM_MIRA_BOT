import discord
from discord.ui import Button, View
from discord import Interaction

from controllers.metier_command_controller import MetierCommandButton
from services.scum_service import send_scum_command
from config.constants import ROLES, CHANNELS, ANNOUNCE_MESSAGES, METIER_NAMES, METIER_COLORS
from utils.action_logger import ActionLogger
from controllers.garage_controller import RavitaillementGarageButton

class ArmurerieOpenButton(Button):
    def __init__(self):
        super().__init__(
            label=f"🔓 Ouverture {METIER_NAMES['armurerie']}",
            style=discord.ButtonStyle.success,
            custom_id="armurerie_open"
        )
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            if not any(role.id == ROLES["armurerie"] for role in interaction.user.roles):
                await interaction.followup.send(f"❌ Rôle {METIER_NAMES['armurerie']} requis.", ephemeral=True)
                return

            success, result = await send_scum_command(
                f"#Announce {ANNOUNCE_MESSAGES['armurerie']['open']}",
                interaction.user.id
            )

            if success:
                await interaction.followup.send(
                    f"✅ Annonce envoyée: {ANNOUNCE_MESSAGES['armurerie']['open']}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "armurerie_announce",
                    "open",
                    "success",
                    ANNOUNCE_MESSAGES['armurerie']['open']
                )
            else:
                await interaction.followup.send(f"❌ Échec: {result}", ephemeral=True)
                self.logger.log_action(
                    interaction.user.id,
                    "armurerie_announce",
                    "open",
                    "failed",
                    result
                )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)
            self.logger.log_action(
                interaction.user.id,
                "armurerie_announce",
                "open",
                "error",
                str(e)
            )

class ArmurerieCloseButton(Button):
    def __init__(self):
        super().__init__(
            label=f"🔒 Fermeture {METIER_NAMES['armurerie']}",
            style=discord.ButtonStyle.danger,
            custom_id="armurerie_close"
        )
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            if not any(role.id == ROLES["armurerie"] for role in interaction.user.roles):
                await interaction.followup.send(f"❌ Rôle {METIER_NAMES['armurerie']} requis.", ephemeral=True)
                return

            success, result = await send_scum_command(
                f"#Announce {ANNOUNCE_MESSAGES['armurerie']['close']}",
                interaction.user.id
            )

            if success:
                await interaction.followup.send(
                    f"✅ Annonce envoyée: {ANNOUNCE_MESSAGES['armurerie']['close']}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "armurerie_announce",
                    "close",
                    "success",
                    ANNOUNCE_MESSAGES['armurerie']['close']
                )
            else:
                await interaction.followup.send(f"❌ Échec: {result}", ephemeral=True)
                self.logger.log_action(
                    interaction.user.id,
                    "armurerie_announce",
                    "close",
                    "failed",
                    result
                )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)
            self.logger.log_action(
                interaction.user.id,
                "armurerie_announce",
                "close",
                "error",
                str(e)
            )

class ArmurerieCommandButton(Button):
    def __init__(self):
        super().__init__(
            label=f"🛡️ Commande {METIER_NAMES['armurerie']}",
            style=discord.ButtonStyle.primary,
            custom_id="armurerie_command"
        )

    async def callback(self, interaction: Interaction):
        if not any(role.id == ROLES["armurerie"] for role in interaction.user.roles):
            await interaction.response.send_message(
                f"❌ Rôle {METIER_NAMES['armurerie']} requis.",
                ephemeral=True
            )
            return

        garagiste_button = RavitaillementGarageButton()
        await garagiste_button.callback(interaction)

def send_armurerie_console_message():
    embed = discord.Embed(
        title=f"🛡️ Console de {METIER_NAMES['armurerie']}",
        description=(
            f"Gérez les annonces et commandes de {METIER_NAMES['armurerie']}.\n\n"
            f"**🔹 Actions disponibles :**\n"
            f"- Ouverture/Fermeture de {METIER_NAMES['armurerie']}\n"
            f"- Commande d'équipement"
        ),
        color=METIER_COLORS["armurerie"]
    )

    view = View(timeout=None)
    view.add_item(ArmurerieOpenButton())
    view.add_item(ArmurerieCloseButton())
    view.add_item(MetierCommandButton("armurerie"))

    return embed, view

async def setup_armurerie_console(bot, channel_id: int):
    channel = bot.get_channel(channel_id)
    if channel:
        embed, view = send_armurerie_console_message()
        await channel.send(embed=embed, view=view)
    else:
        print(f"❌ Canal {channel_id} introuvable.")

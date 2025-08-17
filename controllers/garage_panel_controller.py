import discord
from discord.ui import Button, View
from discord import Interaction

from controllers.metier_command_controller import MetierCommandButton
from services.scum_service import send_scum_command
from config.constants import ROLES, CHANNELS, ANNOUNCE_MESSAGES, METIER_NAMES, METIER_COLORS
from utils.action_logger import ActionLogger
from controllers.garage_controller import RavitaillementGarageButton

class GarageOpenButton(Button):
    def __init__(self):
        super().__init__(
            label=f"🔓 Ouverture {METIER_NAMES['garage']}",
            style=discord.ButtonStyle.success,
            custom_id="garage_open"
        )
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            if not any(role.id == ROLES["garage"] for role in interaction.user.roles):
                await interaction.followup.send(f"❌ Rôle {METIER_NAMES['garage']} requis.", ephemeral=True)
                return

            success, result = await send_scum_command(
                f"#Announce {ANNOUNCE_MESSAGES['garage']['open']}",
                interaction.user.id
            )

            if success:
                await interaction.followup.send(
                    f"✅ Annonce envoyée: {ANNOUNCE_MESSAGES['garage']['open']}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "garage_announce",
                    "open",
                    "success",
                    ANNOUNCE_MESSAGES['garage']['open']
                )
            else:
                await interaction.followup.send(f"❌ Échec: {result}", ephemeral=True)
                self.logger.log_action(
                    interaction.user.id,
                    "garage_announce",
                    "open",
                    "failed",
                    result
                )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)
            self.logger.log_action(
                interaction.user.id,
                "garage_announce",
                "open",
                "error",
                str(e)
            )

class GarageCloseButton(Button):
    def __init__(self):
        super().__init__(
            label=f"🔒 Fermeture {METIER_NAMES['garage']}",
            style=discord.ButtonStyle.danger,
            custom_id="garage_close"
        )
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            if not any(role.id == ROLES["garage"] for role in interaction.user.roles):
                await interaction.followup.send(f"❌ Rôle {METIER_NAMES['garage']} requis.", ephemeral=True)
                return

            success, result = await send_scum_command(
                f"#Announce {ANNOUNCE_MESSAGES['garage']['close']}",
                interaction.user.id
            )

            if success:
                await interaction.followup.send(
                    f"✅ Annonce envoyée: {ANNOUNCE_MESSAGES['garage']['close']}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "garage_announce",
                    "close",
                    "success",
                    ANNOUNCE_MESSAGES['garage']['close']
                )
            else:
                await interaction.followup.send(f"❌ Échec: {result}", ephemeral=True)
                self.logger.log_action(
                    interaction.user.id,
                    "garage_announce",
                    "close",
                    "failed",
                    result
                )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)
            self.logger.log_action(
                interaction.user.id,
                "garage_announce",
                "close",
                "error",
                str(e)
            )

class GarageCommandButton(Button):
    def __init__(self):
        super().__init__(
            label=f"🚚 Commande {METIER_NAMES['garage']}",
            style=discord.ButtonStyle.primary,
            custom_id="garage_command"
        )

    async def callback(self, interaction: Interaction):
        if not any(role.id == ROLES["garage"] for role in interaction.user.roles):
            await interaction.response.send_message(
                f"❌ Rôle {METIER_NAMES['garage']} requis.",
                ephemeral=True
            )
            return

        garagiste_button = RavitaillementGarageButton()
        await garagiste_button.callback(interaction)

def send_garage_console_message():
    embed = discord.Embed(
        title=f"🚗 Console du {METIER_NAMES['garage']}",
        description=(
            f"Gérez les annonces et commandes du {METIER_NAMES['garage']}.\n\n"
            f"**🔹 Actions disponibles :**\n"
            f"- Ouverture/Fermeture du {METIER_NAMES['garage']}\n"
            f"- Commande de produits"
        ),
        color=METIER_COLORS["garage"]
    )

    view = View(timeout=None)
    view.add_item(GarageOpenButton())
    view.add_item(GarageCloseButton())
    view.add_item(MetierCommandButton("garage"))

    return embed, view

async def setup_garage_console(bot, channel_id: int):
    channel = bot.get_channel(channel_id)
    if channel:
        embed, view = send_garage_console_message()
        await channel.send(embed=embed, view=view)
    else:
        print(f"❌ Canal {channel_id} introuvable.")

import discord
from discord.ui import Button, View
from discord import Interaction

from controllers.metier_command_controller import MetierCommandButton
from services.scum_service import send_scum_command
from config.constants import ROLES, CHANNELS, ANNOUNCE_MESSAGES, METIER_NAMES, METIER_COLORS
from utils.action_logger import ActionLogger
from controllers.garage_controller import RavitaillementGarageButton

class RestaurateurOpenButton(Button):
    def __init__(self):
        super().__init__(
            label=f"🔓 Ouverture {METIER_NAMES['restaurateur']}",
            style=discord.ButtonStyle.success,
            custom_id="restaurateur_open"
        )
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            if not any(role.id == ROLES["restaurateur"] for role in interaction.user.roles):
                await interaction.followup.send(f"❌ Rôle {METIER_NAMES['restaurateur']} requis.", ephemeral=True)
                return

            success, result = await send_scum_command(
                f"#Announce {ANNOUNCE_MESSAGES['restaurateur']['open']}",
                interaction.user.id
            )

            if success:
                await interaction.followup.send(
                    f"✅ Annonce envoyée: {ANNOUNCE_MESSAGES['restaurateur']['open']}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "restaurateur_announce",
                    "open",
                    "success",
                    ANNOUNCE_MESSAGES['restaurateur']['open']
                )
            else:
                await interaction.followup.send(f"❌ Échec: {result}", ephemeral=True)
                self.logger.log_action(
                    interaction.user.id,
                    "restaurateur_announce",
                    "open",
                    "failed",
                    result
                )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)
            self.logger.log_action(
                interaction.user.id,
                "restaurateur_announce",
                "open",
                "error",
                str(e)
            )

class RestaurateurCloseButton(Button):
    def __init__(self):
        super().__init__(
            label=f"🔒 Fermeture {METIER_NAMES['restaurateur']}",
            style=discord.ButtonStyle.danger,
            custom_id="restaurateur_close"
        )
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            if not any(role.id == ROLES["restaurateur"] for role in interaction.user.roles):
                await interaction.followup.send(f"❌ Rôle {METIER_NAMES['restaurateur']} requis.", ephemeral=True)
                return

            success, result = await send_scum_command(
                f"#Announce {ANNOUNCE_MESSAGES['restaurateur']['close']}",
                interaction.user.id
            )

            if success:
                await interaction.followup.send(
                    f"✅ Annonce envoyée: {ANNOUNCE_MESSAGES['restaurateur']['close']}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "restaurateur_announce",
                    "close",
                    "success",
                    ANNOUNCE_MESSAGES['restaurateur']['close']
                )
            else:
                await interaction.followup.send(f"❌ Échec: {result}", ephemeral=True)
                self.logger.log_action(
                    interaction.user.id,
                    "restaurateur_announce",
                    "close",
                    "failed",
                    result
                )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)
            self.logger.log_action(
                interaction.user.id,
                "restaurateur_announce",
                "close",
                "error",
                str(e)
            )

class RestaurateurCommandButton(Button):
    def __init__(self):
        super().__init__(
            label=f"🍽️ Commande {METIER_NAMES['restaurateur']}",
            style=discord.ButtonStyle.primary,
            custom_id="restaurateur_command"
        )

    async def callback(self, interaction: Interaction):
        if not any(role.id == ROLES["restaurateur"] for role in interaction.user.roles):
            await interaction.response.send_message(
                f"❌ Rôle {METIER_NAMES['restaurateur']} requis.",
                ephemeral=True
            )
            return

        garagiste_button = RavitaillementGarageButton()
        await garagiste_button.callback(interaction)

def send_restaurateur_console_message():
    embed = discord.Embed(
        title=f"🍽️ Console de {METIER_NAMES['restaurateur']}",
        description=(
            f"Gérez les annonces et commandes de {METIER_NAMES['restaurateur']}.\n\n"
            f"**🔹 Actions disponibles :**\n"
            f"- Ouverture/Fermeture de {METIER_NAMES['restaurateur']}\n"
            f"- Commande de produits"
        ),
        color=METIER_COLORS["restaurateur"]
    )

    view = View(timeout=None)
    view.add_item(RestaurateurOpenButton())
    view.add_item(RestaurateurCloseButton())
    view.add_item(MetierCommandButton("restaurateur"))

    return embed, view

async def setup_restaurateur_console(bot, channel_id: int):
    channel = bot.get_channel(channel_id)
    if channel:
        embed, view = send_restaurateur_console_message()
        await channel.send(embed=embed, view=view)
    else:
        print(f"❌ Canal {channel_id} introuvable.")

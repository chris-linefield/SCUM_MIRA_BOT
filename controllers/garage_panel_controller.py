import discord
from discord.ui import Button, View
from discord import Interaction
from services.scum_service import send_scum_command
from config.settings import settings
from utils.action_logger import ActionLogger

class GarageOpenButton(Button):
    def __init__(self):
        super().__init__(
            label="🔓 Ouverture du Garage",
            style=discord.ButtonStyle.success,
            custom_id="garage_open"
        )
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            # Vérification du rôle
            if not any(role.id == settings.discord_role_garagiste for role in interaction.user.roles):
                await interaction.followup.send("❌ Rôle Garagiste requis.", ephemeral=True)
                return

            # Envoi de l'annonce
            message = "Ouverture du Garage automobile, venez nombreux !"
            success, result = await send_scum_command(
                f"#Announce {message}",
                interaction.user.id
            )

            if success:
                await interaction.followup.send(
                    f"✅ Annonce envoyée: {message}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "garage_announce",
                    "open",
                    "success",
                    message
                )
            else:
                await interaction.followup.send(
                    f"❌ Échec: {result}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "garage_announce",
                    "open",
                    "failed",
                    result
                )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Erreur: {str(e)}",
                ephemeral=True
            )
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
            label="🔒 Fermeture du Garage",
            style=discord.ButtonStyle.danger,
            custom_id="garage_close"
        )
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            # Vérification du rôle
            if not any(role.id == settings.discord_role_garagiste for role in interaction.user.roles):
                await interaction.followup.send("❌ Rôle Garagiste requis.", ephemeral=True)
                return

            # Envoi de l'annonce
            message = "Le Garage automobile ferme ses portes, à bientôt !"
            success, result = await send_scum_command(
                f"#Announce {message}",
                interaction.user.id
            )

            if success:
                await interaction.followup.send(
                    f"✅ Annonce envoyée: {message}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "garage_announce",
                    "close",
                    "success",
                    message
                )
            else:
                await interaction.followup.send(
                    f"❌ Échec: {result}",
                    ephemeral=True
                )
                self.logger.log_action(
                    interaction.user.id,
                    "garage_announce",
                    "close",
                    "failed",
                    result
                )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Erreur: {str(e)}",
                ephemeral=True
            )
            self.logger.log_action(
                interaction.user.id,
                "garage_announce",
                "close",
                "error",
                str(e)
            )

def send_garage_console_message():
    """Crée le message et la vue pour la console du garagiste"""
    embed = discord.Embed(
        title="🚗 Console du Garagiste",
        description=(
            "Gérez les annonces d'ouverture/fermeture du garage.\n\n"
            "**🔹 Actions disponibles :**\n"
            "- Ouverture du garage\n"
            "- Fermeture du garage"
        ),
        color=discord.Color.dark_gold()
    )

    view = View()
    view.add_item(GarageOpenButton())
    view.add_item(GarageCloseButton())

    return embed, view

async def setup_garage_panel(bot, channel_id: int):
    """Envoie le panel de la console du garagiste dans le canal spécifié"""
    channel = bot.get_channel(channel_id)
    if channel:
        embed, view = send_garage_console_message()
        await channel.send(embed=embed, view=view)
    else:
        print(f"❌ Canal {channel_id} introuvable.")

import discord
from discord.ui import Button
from discord import Interaction
from services.bank_service import BankService

class BankBalanceButton(Button):
    def __init__(self):
        super().__init__(
            label="💰 Vérifier mon solde bancaire",
            style=discord.ButtonStyle.blurple,
            custom_id="check_bank_balance"
        )
        self.bank_service = BankService()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            balance = await self.bank_service.get_user_balance(interaction.user.id)

            messages = {
                -1: "❌ Erreur de connexion à la base SCUM (FTP).",
                -2: "❌ Votre SteamID n'est pas lié.",
                -3: "❌ ID SCUM introuvable.",
                -4: "❌ Une erreur inattendue est survenue."
            }

            if balance < 0:
                await interaction.followup.send(messages[balance], ephemeral=True)
            else:
                await interaction.followup.send(
                    f"💰 **Solde actuel** : **{balance}** crédits.\n",
                    ephemeral=True
                )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Une erreur est survenue: {str(e)}",
                ephemeral=True
            )

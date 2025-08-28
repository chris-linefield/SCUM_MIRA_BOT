import discord
from discord.ui import Button
from discord import Interaction
from services.bank_service import BankService
from utils.logger import logger

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
            balance, message = await self.bank_service.get_user_balance(interaction.user.id)
            if balance < 0:
                await interaction.followup.send(f"❌ **Erreur** : {message}", ephemeral=True)
            else:
                await interaction.followup.send(f"💰 **Solde actuel** : **{balance}** crédits.", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur BankBalanceButton (user {interaction.user.id}): {str(e)}", exc_info=True)
            await interaction.followup.send("❌ **Erreur critique** : Impossible de récupérer votre solde.", ephemeral=True)

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
        # 1. Vérifie si l'interaction a déjà été répondue
        if interaction.response.is_done():
            await interaction.followup.send("⚠️ L'interaction a expiré. Veuillez réessayer.", ephemeral=True)
            return

        # 2. Répond immédiatement pour éviter le timeout
        await interaction.response.defer(ephemeral=True)

        try:
            # 3. Récupère le solde
            balance = await self.bank_service.get_user_balance(interaction.user.id)

            # 4. Messages d'erreur standardisés
            messages = {
                -1: "❌ **Erreur M.I.R.A** : Impossible de se connecter à la base de données SCUM (FTP).",
                -2: "❌ **Erreur M.I.R.A** : Votre SteamID n'est pas lié.",
                -3: "❌ **Erreur M.I.R.A** : ID SCUM introuvable. Contactez un administrateur.",
                -4: "❌ **Erreur M.I.R.A** : Une erreur inattendue est survenue. Réessayez plus tard.",
            }

            if balance < 0:
                await interaction.followup.send(messages.get(balance, "❌ **Erreur M.I.R.A** : Code d'erreur inconnu."), ephemeral=True)
            else:
                await interaction.followup.send(f"💰 **Solde actuel** : **{balance}** crédits.", ephemeral=True)

        except Exception as e:
            logger.error(f"Erreur BankBalanceButton (user {interaction.user.id}): {str(e)}", exc_info=True)
            await interaction.followup.send("❌ **Erreur M.I.R.A** : Impossible de récupérer votre solde. Réessayez plus tard.", ephemeral=True)
import discord
from discord.ext import commands  # Ajout de l'import correct
from discord.ui import View, Button, Select
from services.scum_service import ScumService
from services.game_client import GameClient
from repositories.user_repository import UserRepository
from repositories.scum_repository import get_bank_balance, update_bank_balance
from services.delivery_service import schedule_delivery
from config.constants import ITEM_PRICES, MAX_QUANTITY, METIER_ITEMS, ANNOUNCE_MESSAGES, DELIVERY_POSITIONS
from utils.logger import logger
import random

class ShopView(View):
    def __init__(self, merchant_type: str, bot: commands.Bot):
        super().__init__(timeout=None)
        self.merchant_type = merchant_type
        self.bot = bot
        self.add_item(OpenShopButton(merchant_type, bot))
        self.add_item(CloseShopButton(merchant_type, bot))
        self.add_item(CheckBalanceButton(bot))
        self.add_item(BuyItemButton(merchant_type, bot))
        if "vehicles" in METIER_ITEMS[merchant_type]:
            self.add_item(BuyVehicleButton(merchant_type, bot))

class OpenShopButton(Button):
    def __init__(self, merchant_type: str, bot: commands.Bot):
        super().__init__(label="Ouverture du commerce", style=discord.ButtonStyle.success, custom_id=f"open_shop_{merchant_type}")
        self.merchant_type = merchant_type
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        message = ANNOUNCE_MESSAGES[self.merchant_type]["open"]
        if await GameClient.announce(message):
            await interaction.followup.send(f"Annonce d'ouverture envoyée: {message}", ephemeral=True)
        else:
            await interaction.followup.send("Erreur lors de l'envoi de l'annonce.", ephemeral=True)

class CloseShopButton(Button):
    def __init__(self, merchant_type: str, bot: commands.Bot):
        super().__init__(label="Fermeture du commerce", style=discord.ButtonStyle.danger, custom_id=f"close_shop_{merchant_type}")
        self.merchant_type = merchant_type
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        message = ANNOUNCE_MESSAGES[self.merchant_type]["close"]
        if await GameClient.announce(message):
            await interaction.followup.send(f"Annonce de fermeture envoyée: {message}", ephemeral=True)
        else:
            await interaction.followup.send("Erreur lors de l'envoi de l'annonce.", ephemeral=True)

class CheckBalanceButton(Button):
    def __init__(self, bot: commands.Bot):
        super().__init__(label="Consulter mon solde", style=discord.ButtonStyle.blurple, custom_id="check_balance")
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_repo = UserRepository()
        user = user_repo.get_user(interaction.user.id)
        if not user:
            await interaction.followup.send(
                "⚠️ **Erreur** : Vous devez d'abord vous enregistrer avec la commande `!register`.",
                ephemeral=True
            )
            return

        balance = get_bank_balance(user.steam_id)
        if balance is None:
            await interaction.followup.send(
                "⚠️ **Erreur** : Impossible de récupérer votre solde bancaire. Veuillez réessayer plus tard.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="💰 Solde Bancaire",
            description=f"Votre solde bancaire actuel est de **{balance}**.",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"SteamID: {user.steam_id} | {user.name}")
        await interaction.followup.send(embed=embed, ephemeral=True)

class BuyItemButton(Button):
    def __init__(self, merchant_type: str, bot: commands.Bot):
        super().__init__(label="Commander du matériel", style=discord.ButtonStyle.green, custom_id=f"buy_item_{merchant_type}")
        self.merchant_type = merchant_type
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_repo = UserRepository()
        user = user_repo.get_user(interaction.user.id)
        if not user:
            await interaction.followup.send("Vous devez d'abord vous enregistrer avec `!register`.", ephemeral=True)
            return

        merchant_items = METIER_ITEMS[self.merchant_type]["materials"] if isinstance(METIER_ITEMS[self.merchant_type], dict) else METIER_ITEMS[self.merchant_type]
        if not merchant_items:
            await interaction.followup.send("Aucun matériel disponible pour ce marchand.", ephemeral=True)
            return

        options = [discord.SelectOption(label=item, value=item) for item in merchant_items]
        select = Select(placeholder="Choisissez un item", options=options, custom_id=f"select_item_{self.merchant_type}")
        view = View()
        view.add_item(select)
        await interaction.followup.send("Sélectionnez un item:", view=view, ephemeral=True)

        async def select_callback(select_interaction: discord.Interaction):
            if select_interaction.user != interaction.user:
                return
            item_id = select.values[0]
            await select_interaction.response.send_modal(BuyItemModal(item_id, user.steam_id, self.merchant_type, user.discord_id, self.bot))

        select.callback = select_callback

class BuyItemModal(discord.ui.Modal):
    def __init__(self, item_id: str, user_steam_id: str, merchant_type: str, user_discord_id: int, bot: commands.Bot):
        super().__init__(title=f"Achat: {item_id}")
        self.item_id = item_id
        self.user_steam_id = user_steam_id
        self.merchant_type = merchant_type
        self.user_discord_id = user_discord_id
        self.bot = bot
        self.count = discord.ui.TextInput(
            label=f"Quantité (1-{MAX_QUANTITY})",
            placeholder="1",
            min_length=1,
            max_length=2,
            custom_id="item_count"
        )
        self.add_item(self.count)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        count = int(self.count.value)
        price = ITEM_PRICES[self.item_id] * count
        balance = get_bank_balance(self.user_steam_id)

        if balance < price:
            await interaction.followup.send("⚠️ **Erreur** : Solde insuffisant pour effectuer cet achat.",
                                            ephemeral=True)
            return

        new_balance = balance - price
        if not update_bank_balance(self.user_steam_id, new_balance):
            await interaction.followup.send("⚠️ **Erreur** : Impossible de mettre à jour votre solde.", ephemeral=True)
            return

        if not await ScumService.buy_item(self.user_steam_id, self.item_id, count, price):
            await interaction.followup.send("⚠️ **Erreur** : Erreur lors de l'achat.", ephemeral=True)
            return

        new_balance = get_bank_balance(self.user_steam_id)

        # Planifier la livraison
        if not await schedule_delivery(self.bot, self.user_discord_id, self.user_steam_id, self.item_id, count):
            await interaction.followup.send("⚠️ **Erreur** : Erreur lors de la planification de la livraison.",
                                            ephemeral=True)
            return

        # Envoyer un message privé immersif et roleplay
        user = await self.bot.fetch_user(self.user_discord_id)
        delivery_position = random.choice(list(DELIVERY_POSITIONS.keys()))

        # Message immersif et roleplay
        message = (
            f"📜 **Contrat de Livraison M.I.R.A** 📜\n\n"
            f"Cher Client,\n\n"
            f"Votre commande de **{count}x {self.item_id}** a été enregistrée avec succès.\n"
            f"Le montant de **{price}** a été prélevé de votre compte.\n\n"
            f"📍 **Lieu de livraison** : {delivery_position}\n"
            f"⏰ **Heure de livraison** : Dans 20 minutes\n\n"
            f"Veuillez vous rendre sur place pour récupérer votre commande.\n"
            f"En cas de problème, contactez le service client M.I.R.A.\n\n"
            f"Cordialement,\n"
            f"**M.I.R.A Logistics**"
        )

        await user.send(message)

        await interaction.followup.send(
            f"Commande de {count}x {self.item_id} enregistrée !\nLivraison prévue à {delivery_position} dans 20 minutes.",
            ephemeral=True)

class BuyVehicleButton(Button):
    def __init__(self, merchant_type: str, bot: commands.Bot):
        super().__init__(label="Commander un véhicule", style=discord.ButtonStyle.green, custom_id=f"buy_vehicle_{merchant_type}")
        self.merchant_type = merchant_type
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_repo = UserRepository()
        user = user_repo.get_user(interaction.user.id)
        if not user:
            await interaction.followup.send("Vous devez d'abord vous enregistrer avec `!register`.", ephemeral=True)
            return

        merchant_vehicles = METIER_ITEMS[self.merchant_type]["vehicles"]
        if not merchant_vehicles:
            await interaction.followup.send("Aucun véhicule disponible pour ce marchand.", ephemeral=True)
            return

        options = [discord.SelectOption(label=vehicle, value=vehicle) for vehicle in merchant_vehicles]
        select = VehicleSelect(user.steam_id, options, self.merchant_type, user.discord_id, self.bot)
        view = View()
        view.add_item(select)
        await interaction.followup.send("Sélectionnez un véhicule:", view=view, ephemeral=True)

class VehicleSelect(Select):
    def __init__(self, user_steam_id: str, options: list, merchant_type: str, user_discord_id: int, bot: commands.Bot):
        super().__init__(placeholder="Choisissez un véhicule", options=options, custom_id=f"select_vehicle_{merchant_type}")
        self.user_steam_id = user_steam_id
        self.merchant_type = merchant_type
        self.user_discord_id = user_discord_id
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vehicle_id = self.values[0]
        price = ITEM_PRICES[vehicle_id]
        balance = get_bank_balance(self.user_steam_id)

        if balance < price:
            await interaction.followup.send("⚠️ **Erreur** : Solde insuffisant pour effectuer cet achat.",
                                            ephemeral=True)
            return

        new_balance = balance - price
        if not update_bank_balance(self.user_steam_id, new_balance):
            await interaction.followup.send("⚠️ **Erreur** : Impossible de mettre à jour votre solde.", ephemeral=True)
            return

        if not await ScumService.buy_vehicle(self.user_steam_id, vehicle_id, price):
            await interaction.followup.send("⚠️ **Erreur** : Erreur lors de l'achat du véhicule.", ephemeral=True)
            return

        new_balance = get_bank_balance(self.user_steam_id)

        # Envoyer un message privé immersif et roleplay
        user = await self.bot.fetch_user(self.user_discord_id)

        # Message immersif et roleplay
        message = (
            f"📜 **Contrat d'Achat de Véhicule M.I.R.A** 📜\n\n"
            f"Cher Client,\n\n"
            f"Votre achat du véhicule **{vehicle_id}** a été finalisé avec succès.\n"
            f"Le montant de **{price}** a été prélevé de votre compte.\n\n"
            f"Votre véhicule est prêt à être récupéré à la position de spawn.\n"
            f"En cas de problème, contactez le service client M.I.R.A.\n\n"
            f"Cordialement,\n"
            f"**M.I.R.A Vehicles**"
        )

        await user.send(message)

        await interaction.followup.send(
            f"Achat du véhicule {vehicle_id} effectué !\nNouveau solde : **{new_balance}**.", ephemeral=True)
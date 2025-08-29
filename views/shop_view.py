import discord
from discord.ui import View, Button, Select
from services.scum_service import ScumService
from services.game_client import GameClient
from repositories.user_repository import UserRepository
from repositories.scum_repository import get_user_balance
from config.constants import ITEM_PRICES, MAX_QUANTITY, METIER_ITEMS, ANNOUNCE_MESSAGES
from utils.logger import logger

class ShopView(View):
    def __init__(self, merchant_type: str):
        super().__init__(timeout=None)
        self.merchant_type = merchant_type
        self.add_item(OpenShopButton(merchant_type))
        self.add_item(CloseShopButton(merchant_type))
        self.add_item(CheckBalanceButton())
        self.add_item(BuyItemButton(merchant_type))
        if any(item.startswith("BP_") for item in METIER_ITEMS[merchant_type]):
            self.add_item(BuyVehicleButton(merchant_type))

class OpenShopButton(Button):
    def __init__(self, merchant_type: str):
        super().__init__(label="Ouverture du commerce", style=discord.ButtonStyle.success, custom_id=f"open_shop_{merchant_type}")
        self.merchant_type = merchant_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        message = ANNOUNCE_MESSAGES[self.merchant_type]["open"]
        if await GameClient.announce(message):
            await interaction.followup.send(f"Annonce d'ouverture envoyée: {message}", ephemeral=True)
        else:
            await interaction.followup.send("Erreur lors de l'envoi de l'annonce.", ephemeral=True)

class CloseShopButton(Button):
    def __init__(self, merchant_type: str):
        super().__init__(label="Fermeture du commerce", style=discord.ButtonStyle.danger, custom_id=f"close_shop_{merchant_type}")
        self.merchant_type = merchant_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        message = ANNOUNCE_MESSAGES[self.merchant_type]["close"]
        if await GameClient.announce(message):
            await interaction.followup.send(f"Annonce de fermeture envoyée: {message}", ephemeral=True)
        else:
            await interaction.followup.send("Erreur lors de l'envoi de l'annonce.", ephemeral=True)

class CheckBalanceButton(Button):
    def __init__(self):
        super().__init__(label="Consulter mon solde", style=discord.ButtonStyle.blurple, custom_id="check_balance")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_repo = UserRepository()
        user = user_repo.get_user(interaction.user.id)
        if not user:
            await interaction.followup.send("Vous devez d'abord vous enregistrer avec `!register`.", ephemeral=True)
            return

        balance = get_user_balance(user.steam_id)
        await interaction.followup.send(f"Votre solde bancaire est de: {balance}", ephemeral=True)

class BuyItemButton(Button):
    def __init__(self, merchant_type: str):
        super().__init__(label="Commander du matériel", style=discord.ButtonStyle.green, custom_id=f"buy_item_{merchant_type}")
        self.merchant_type = merchant_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_repo = UserRepository()
        user = user_repo.get_user(interaction.user.id)
        if not user:
            await interaction.followup.send("Vous devez d'abord vous enregistrer avec `!register`.", ephemeral=True)
            return

        merchant_items = [item for item in METIER_ITEMS[self.merchant_type] if not item.startswith("BP_")]
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
            await select_interaction.response.send_modal(BuyItemModal(item_id, user.steam_id, self.merchant_type))

        select.callback = select_callback

class BuyItemModal(discord.ui.Modal):
    def __init__(self, item_id: str, user_steam_id: str, merchant_type: str):
        super().__init__(title=f"Achat: {item_id}")
        self.item_id = item_id
        self.user_steam_id = user_steam_id
        self.merchant_type = merchant_type
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
        if await ScumService.buy_item(self.user_steam_id, self.item_id, count, price):
            await interaction.followup.send(f"Achat de {count}x {self.item_id} effectué !", ephemeral=True)
        else:
            await interaction.followup.send("Solde insuffisant ou erreur lors de l'achat.", ephemeral=True)

class BuyVehicleButton(Button):
    def __init__(self, merchant_type: str):
        super().__init__(label="Commander un véhicule", style=discord.ButtonStyle.green, custom_id=f"buy_vehicle_{merchant_type}")
        self.merchant_type = merchant_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_repo = UserRepository()
        user = user_repo.get_user(interaction.user.id)
        if not user:
            await interaction.followup.send("Vous devez d'abord vous enregistrer avec `!register`.", ephemeral=True)
            return

        merchant_vehicles = [item for item in METIER_ITEMS[self.merchant_type] if item.startswith("BP_")]
        if not merchant_vehicles:
            await interaction.followup.send("Aucun véhicule disponible pour ce marchand.", ephemeral=True)
            return

        options = [discord.SelectOption(label=vehicle, value=vehicle) for vehicle in merchant_vehicles]
        select = VehicleSelect(user.steam_id, options, self.merchant_type)
        view = View()
        view.add_item(select)
        await interaction.followup.send("Sélectionnez un véhicule:", view=view, ephemeral=True)

class VehicleSelect(Select):
    def __init__(self, user_steam_id: str, options: list, merchant_type: str):
        super().__init__(placeholder="Choisissez un véhicule", options=options, custom_id=f"select_vehicle_{merchant_type}")
        self.user_steam_id = user_steam_id
        self.merchant_type = merchant_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vehicle_id = self.values[0]
        if await ScumService.buy_vehicle(self.user_steam_id, vehicle_id, ITEM_PRICES[vehicle_id]):
            await interaction.followup.send(f"Achat du véhicule {vehicle_id} effectué !", ephemeral=True)
        else:
            await interaction.followup.send("Solde insuffisant ou erreur lors de l'achat.", ephemeral=True)
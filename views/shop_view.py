import discord
from discord.ext import commands
from discord.ui import View, Button, Select
from services.scum_service import ScumService
from services.game_client import GameClient
from repositories.user_repository import UserRepository
from repositories.scum_repository import get_bank_balance, update_bank_balance
from repositories.ftp_repository import copy_tables_to_local_db
from config.constants import ITEM_PRICES, MAX_QUANTITY, METIER_ITEMS, ANNOUNCE_MESSAGES, MERCHANT_DELIVERY_POSITIONS, PACK_ITEMS
from utils.logger import logger
import asyncio

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
        if "packs" in METIER_ITEMS[merchant_type]:
            self.add_item(BuyPackButton(merchant_type, bot))

class OpenShopButton(Button):
    def __init__(self, merchant_type: str, bot: commands.Bot):
        super().__init__(label="Ouverture du commerce", style=discord.ButtonStyle.success, custom_id=f"open_shop_{merchant_type}")
        self.merchant_type = merchant_type
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        copy_tables_to_local_db()
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
        copy_tables_to_local_db()
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

        async def select_callback(select_interaction: discord.Interaction):
            if select_interaction.user != interaction.user:
                return
            item_id = select.values[0]
            await select_interaction.response.send_modal(BuyItemModal(item_id, user.steam_id, self.merchant_type, user.discord_id, self.bot))

        select.callback = select_callback
        await interaction.followup.send("Sélectionnez un item:", view=view, ephemeral=True)

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
            await interaction.followup.send("⚠️ **Erreur** : Solde insuffisant pour effectuer cet achat.", ephemeral=True)
            return
        success = await ScumService.buy_item(self.user_steam_id, self.item_id, count, price, self.merchant_type)
        if not success:
            await interaction.followup.send("⚠️ **Erreur** : Erreur lors de l'achat.", ephemeral=True)
            return
        new_balance = get_bank_balance(self.user_steam_id)
        user = await self.bot.fetch_user(self.user_discord_id)
        message = (
            f"📜 **Contrat de Livraison M.I.R.A** 📜\n\n"
            f"Cher Client,\n\n"
            f"Votre commande de **{count}x {self.item_id}** a été traitée avec succès.\n"
            f"Le montant de **{price}** a été prélevé de votre compte.\n\n"
            f"Votre commande est prête à être récupérée au **{self.merchant_type}**. \n\n"
            f"En cas de problème, contactez le service client M.I.R.A.\n\n"
            f"Cordialement,\n"
            f"**M.I.R.A Logistics**"
        )
        await user.send(message)
        await interaction.followup.send(f"Achat de {count}x {self.item_id} effectué !\nNouveau solde : **{new_balance}**.", ephemeral=True)

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
            await interaction.followup.send("⚠️ **Erreur** : Solde insuffisant pour effectuer cet achat.", ephemeral=True)
            return
        success = await ScumService.buy_vehicle(self.user_steam_id, vehicle_id, price)
        if not success:
            await interaction.followup.send("⚠️ **Erreur** : Erreur lors de l'achat du véhicule.", ephemeral=True)
            return
        new_balance = get_bank_balance(self.user_steam_id)
        user = await self.bot.fetch_user(self.user_discord_id)
        message = (
            f"📜 **Contrat d'Achat de Véhicule M.I.R.A** 📜\n\n"
            f"Cher Client,\n\n"
            f"Votre achat du véhicule **{vehicle_id}** a été finalisé avec succès.\n"
            f"Le montant de **{price}** a été prélevé de votre compte.\n\n"
            f"Votre véhicule est prêt à être récupéré.\n"
            f"En cas de problème, contactez le service client M.I.R.A.\n\n"
            f"Cordialement,\n"
            f"**M.I.R.A Vehicles**"
        )
        await user.send(message)
        await interaction.followup.send(f"Achat du véhicule {vehicle_id} effectué !\nNouveau solde : **{new_balance}**.", ephemeral=True)

class BuyPackButton(Button):
    def __init__(self, merchant_type: str, bot: commands.Bot):
        super().__init__(label="Commander un pack", style=discord.ButtonStyle.green, custom_id=f"buy_pack_{merchant_type}")
        self.merchant_type = merchant_type
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_repo = UserRepository()
        user = user_repo.get_user(interaction.user.id)
        if not user:
            await interaction.followup.send("Vous devez d'abord vous enregistrer avec `!register`.", ephemeral=True)
            return
        merchant_packs = METIER_ITEMS[self.merchant_type].get("packs", [])
        if not merchant_packs:
            await interaction.followup.send("Aucun pack disponible pour ce marchand.", ephemeral=True)
            return
        options = [discord.SelectOption(label=pack.replace("_", " ").title(), value=pack) for pack in merchant_packs]
        select = Select(placeholder="Choisissez un pack", options=options, custom_id=f"select_pack_{self.merchant_type}")
        view = View()
        view.add_item(select)

        async def select_callback(select_interaction: discord.Interaction):
            if select_interaction.user != interaction.user:
                return
            pack_id = select.values[0]
            await select_interaction.response.send_modal(BuyPackModal(pack_id, user.steam_id, self.merchant_type, user.discord_id, self.bot))

        select.callback = select_callback
        await interaction.followup.send("Sélectionnez un pack:", view=view, ephemeral=True)

class BuyPackModal(discord.ui.Modal):
    def __init__(self, pack_id: str, user_steam_id: str, merchant_type: str, user_discord_id: int, bot: commands.Bot):
        super().__init__(title=f"Achat: {pack_id.replace('_', ' ').title()}")
        self.pack_id = pack_id
        self.user_steam_id = user_steam_id
        self.merchant_type = merchant_type
        self.user_discord_id = user_discord_id
        self.bot = bot
        self.count = discord.ui.TextInput(
            label="Quantité (1)",
            placeholder="1",
            min_length=1,
            max_length=1,
            custom_id="pack_count",
            default="1"
        )
        self.add_item(self.count)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        count = int(self.count.value)
        price = ITEM_PRICES[self.pack_id] * count
        balance = get_bank_balance(self.user_steam_id)
        if balance < price:
            await interaction.followup.send("⚠️ **Erreur** : Solde insuffisant pour effectuer cet achat.", ephemeral=True)
            return

        success = await self.buy_pack(self.user_steam_id, self.pack_id, count, price, self.merchant_type)
        if not success:
            await interaction.followup.send("⚠️ **Erreur** : Erreur lors de l'achat du pack. Vérifiez les logs.", ephemeral=True)
            return

        new_balance = get_bank_balance(self.user_steam_id)
        user = await self.bot.fetch_user(self.user_discord_id)
        message = (
            f"📜 **Contrat de Livraison M.I.R.A** 📜\n\n"
            f"Cher Client,\n\n"
            f"Votre commande du pack **{self.pack_id.replace('_', ' ').title()}** a été traitée avec succès.\n"
            f"Le montant de **{price}** a été prélevé de votre compte.\n\n"
            f"Votre pack est prêt à être récupéré au **{self.merchant_type}**. \n\n"
            f"En cas de problème, contactez le service client M.I.R.A.\n\n"
            f"Cordialement,\n"
            f"**M.I.R.A Logistics**"
        )
        await user.send(message)
        await interaction.followup.send(f"Achat du pack {self.pack_id.replace('_', ' ').title()} effectué !\nNouveau solde : **{new_balance}**.", ephemeral=True)

    async def buy_pack(self, user_steam_id: str, pack_id: str, count: int, price: int, merchant_type: str) -> bool:
        # 1. Vérifier la position de livraison
        if merchant_type not in MERCHANT_DELIVERY_POSITIONS or MERCHANT_DELIVERY_POSITIONS[merchant_type] == (0, 0, 0):
            logger.error(f"Position de livraison non définie pour {merchant_type}.")
            return False

        # 2. Vérifier le solde
        balance = get_bank_balance(user_steam_id)
        if balance < price:
            logger.error(f"Solde insuffisant pour {user_steam_id} (pack {pack_id}).")
            return False

        # 3. Préparer la position de livraison
        x, y, z = MERCHANT_DELIVERY_POSITIONS[merchant_type]

        # 4. Téléroportation
        teleport_command = f"#Teleport {x} {y} {z}"
        success, _ = await GameClient.send_command(teleport_command)
        if not success:
            logger.error(f"Échec de la téléportation pour {merchant_type} (pack {pack_id}).")
            return False
        await asyncio.sleep(10)  # Temps de chargement de la zone

        # 5. Spawn de tous les items du pack (avec délai)
        for item_id in PACK_ITEMS[pack_id]:
            spawn_command = f"#SpawnItem {item_id} {count}"
            success, _ = await GameClient.send_command(spawn_command)
            if not success:
                logger.error(f"Échec du spawn de {item_id} pour le pack {pack_id}.")
                return False
            await asyncio.sleep(2)  # Délai de 2 secondes entre chaque spawn

        # 6. Mise à jour du solde (après succès)
        new_balance = balance - price
        set_balance_command = f"#SetCurrencyBalance Normal {new_balance} {user_steam_id}"
        success, _ = await GameClient.send_command(set_balance_command)
        if not success:
            logger.error(f"Échec de la mise à jour du solde pour {user_steam_id} (pack {pack_id}).")
            return False

        if not update_bank_balance(user_steam_id, new_balance):
            logger.error(f"Échec de la mise à jour locale du solde pour {user_steam_id} (pack {pack_id}).")
            return False

        # 7. Annonce en jeu
        pack_name = pack_id.replace("_", " ").title()
        announce_message = f"#Announce Pack {pack_name} livré à {merchant_type} pour {user_steam_id} !"
        await GameClient.announce(announce_message)

        return True
import discord
import pydirectinput
from discord.ui import Button, Select, View, Modal, TextInput
from discord import Interaction, Embed
from config.constants import ITEM_PRICES, METIER_NAMES, MAX_QUANTITY, METIER_COLORS, ROLES, METIER_ITEMS
from repositories.scum_repository import logger
from services.bank_service import BankService
from services.scum_service import send_scum_command
from services.delivery_service import DeliveryService
from config.constants import DELIVERY_POSITIONS
from repositories.user_repository import UserRepository
import random
import asyncio
from datetime import datetime, timedelta

class MetierItemSelectView(View):
    def __init__(self, bank_service: BankService, user_repo: UserRepository, user_id: int, metier: str):
        super().__init__(timeout=180)
        self.bank_service = bank_service
        self.user_repo = user_repo
        self.user_id = user_id
        self.metier = metier

        # Crée un select avec uniquement les items du métier
        options = []
        for item in METIER_ITEMS[metier]:
            item_name = item.replace("_", " ").title()
            options.append(discord.SelectOption(label=item_name, value=item))

        self.select = Select(
            placeholder=f"Sélectionnez un item ({METIER_NAMES[metier]})",
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: Interaction):
        await interaction.response.send_modal(
            MetierQuantityModal(
                self.select.values[0],
                self.bank_service,
                self.user_repo,
                interaction,
                self.user_id,
                self.metier
            )
        )

class MetierQuantityModal(Modal):
    def __init__(self, item: str, bank_service: BankService, user_repo: UserRepository,
                 interaction: Interaction, user_id: int, metier: str):
        super().__init__(title=f"Quantité pour {item.replace('_', ' ').title()}")
        self.item = item
        self.bank_service = bank_service
        self.user_repo = user_repo
        self.interaction = interaction
        self.user_id = user_id
        self.metier = metier
        self.quantity = TextInput(
            label=f"Quantité (1-{MAX_QUANTITY})",
            placeholder="Ex: 5",
            min_length=1,
            max_length=2
        )
        self.add_item(self.quantity)

    async def on_submit(self, interaction: Interaction):
        # 1. Vérifie si l'interaction a déjà été répondue
        if interaction.response.is_done():
            await interaction.followup.send("⚠️ L'interaction a expiré. Veuillez réessayer.", ephemeral=True)
            return

        # 2. Répond immédiatement pour éviter le timeout
        await interaction.response.defer(ephemeral=True)

        try:
            quantity = int(self.quantity.value)
            if not 1 <= quantity <= MAX_QUANTITY:
                await interaction.followup.send(
                    f"❌ La quantité doit être entre 1 et {MAX_QUANTITY}.",
                    ephemeral=True
                )
                return

            # 3. Calcul du coût total
            item_price = ITEM_PRICES.get(self.item, 0)
            total_cost = quantity * item_price
            await interaction.followup.send(
                f"✅ Commande enregistrée! Coût total: {total_cost}€ (vérifiez vos MP).",
                ephemeral=True
            )

            # 4. Lance le traitement en arrière-plan
            asyncio.create_task(self.process_delivery(interaction, quantity, total_cost))

        except ValueError:
            await interaction.followup.send("❌ Veuillez entrer un nombre valide.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)
            logger.error(f"Erreur dans MetierQuantityModal: {str(e)}", exc_info=True)

    async def process_delivery(self, interaction: Interaction, quantity: int, total_cost: int):
        try:
            # Message de progression initial
            progress_msg = await interaction.user.send("🔄 Initialisation de la livraison...")

            # Vérification de l'utilisateur
            user = self.user_repo.get_user(self.user_id)
            if not user or 'steam_id' not in user:
                await progress_msg.edit(content="❌ SteamID non lié.")
                return

            # Vérification du solde
            await progress_msg.edit(content="💰 Vérification du solde...")
            balance = await self.bank_service.get_user_balance(self.user_id)
            if balance < 0:
                await progress_msg.edit(content="❌ Erreur de connexion à la base SCUM.")
                return
            if balance < total_cost:
                await progress_msg.edit(content=f"❌ Solde insuffisant ({balance}€).")
                return

            # Retrait des fonds
            await progress_msg.edit(content="💸 Retrait des fonds...")
            new_balance = balance - total_cost
            success, _ = await self.bank_service.withdraw(self.user_id, total_cost)
            if not success:
                await progress_msg.edit(content="❌ Erreur lors du retrait.")
                return

            # Mise à jour du solde dans SCUM
            await progress_msg.edit(content="🔄 Mise à jour du solde SCUM...")
            success, message = await send_scum_command(
                f"#SetCurrencyBalance Normal {new_balance} {user['steam_id']}",
                self.user_id
            )
            if not success:
                await progress_msg.edit(content=f"⚠️ {message}")
                return

            pydirectinput.press('enter')
            await asyncio.sleep(0.5)

            # Création de la livraison
            await progress_msg.edit(content="📦 Création de la livraison...")
            delivery_location = random.choice(list(DELIVERY_POSITIONS.keys()))
            coords = DELIVERY_POSITIONS[delivery_location]
            delivery_service = DeliveryService()
            delivery_id = delivery_service.create_delivery(
                self.user_id, self.item, quantity, total_cost,
                delivery_location, coords, user['steam_id']
            )

            # Message final avec timer
            await progress_msg.edit(content="⏳ Livraison en cours (20 min)...")
            embed = Embed(
                title="📦 Livraison en cours",
                description=f"⏳ Temps restant: **20m 00s**\n💰 Coût total: {total_cost}€",
                color=METIER_COLORS[self.metier]
            )
            embed.add_field(name="📍 Position", value=delivery_location)
            embed.add_field(name="💰 Coût", value=f"{total_cost}€ (solde: {new_balance}€)")
            embed.add_field(name="📦 Item", value=f"{self.item.replace('_', ' ').title()} x{quantity}")
            embed.set_footer(text=f"ID: {delivery_id}")

            timer_message = await interaction.user.send(embed=embed)

            # Configuration du timer
            ends_at = datetime.now() + timedelta(minutes=20)
            delivery_service.update_ends_at(delivery_id, ends_at.strftime("%Y-%m-%d %H:%M:%S"))

            async def update_timer():
                while True:
                    delivery = delivery_service.get_delivery(delivery_id)
                    if not delivery or delivery.get('is_cancelled', False) or delivery.get('is_completed', False):
                        return

                    try:
                        ends_at_str = str(delivery['ends_at']).split('.')[0]
                        ends_at = datetime.strptime(ends_at_str, "%Y-%m-%d %H:%M:%S")
                        remaining = (ends_at - datetime.now()).total_seconds()

                        if remaining <= 0:
                            break

                        embed.description = f"⏳ Temps restant: {int(remaining//60)}m {int(remaining%60)}s"
                        await timer_message.edit(embed=embed)
                        await asyncio.sleep(30)
                    except Exception as e:
                        print(f"Erreur timer: {e}")
                        break

                if not delivery_service.get_delivery(delivery_id).get('is_cancelled', False):
                    await progress_msg.edit(content="📢 Annonce de livraison dans 5 min...")

                    success, message = await send_scum_command(
                        f"#announce Livraison pour {interaction.user.name} à {delivery_location} dans 5 minutes!",
                        self.user_id
                    )
                    if not success:
                        await interaction.user.send(f"⚠️ {message} (annonce)")

                    await asyncio.sleep(5*60)

                    await progress_msg.edit(content="🚛 Livraison en cours...")

                    success, message = await send_scum_command(
                        f"#Teleport {coords[0]} {coords[1]} {coords[2]}",
                        self.user_id
                    )
                    if not success:
                        await interaction.user.send(f"⚠️ {message} (téléportation)")
                        return

                    await asyncio.sleep(5)

                    for i in range(quantity):
                        await progress_msg.edit(content=f"📦 Spawn des items ({i+1}/{quantity})...")
                        success, message = await send_scum_command(
                            f"#SpawnItem {self.item} {quantity}",
                            self.user_id
                        )
                        if not success:
                            await interaction.user.send(f"⚠️ {message} (spawn {i+1}/{quantity})")
                        await asyncio.sleep(1.5)

                    embed.description = "🚛 Livraison effectuée!"
                    embed.color = METIER_COLORS[self.metier]
                    await timer_message.edit(embed=embed, view=None)
                    await progress_msg.edit(content="✅ Livraison terminée!")
                    delivery_service.complete_delivery(delivery_id)

            asyncio.create_task(update_timer())

        except Exception as e:
            await interaction.user.send(f"❌ Erreur: {str(e)}")
            import traceback
            print(traceback.format_exc())

class MetierCommandButton(Button):
    def __init__(self, metier: str):
        super().__init__(
            label=f"🛒 Commande {METIER_NAMES[metier]}",
            style=discord.ButtonStyle.primary,
            custom_id=f"{metier}_command"
        )
        self.metier = metier

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            # Vérification du rôle
            if not any(role.id == ROLES[self.metier] for role in interaction.user.roles):
                await interaction.followup.send(
                    f"❌ Rôle {METIER_NAMES[self.metier]} requis.",
                    ephemeral=True
                )
                return

            # Affichage des items disponibles pour ce métier
            bank_service = BankService()
            user_repo = UserRepository()

            await interaction.followup.send(
                f"📦 Sélectionnez un item ({METIER_NAMES[self.metier]}):",
                view=MetierItemSelectView(bank_service, user_repo, interaction.user.id, self.metier),
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)

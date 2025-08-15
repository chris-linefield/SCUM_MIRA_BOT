# controllers/garage_controller.py
from datetime import datetime, timedelta
import discord
import random
import asyncio
from discord.ui import Button, Select, View, Modal, TextInput
from discord import Interaction, Embed
from config.constants import DELIVERY_POSITIONS
from services.bank_service import BankService
from services.scum_service import send_scum_command
from services.delivery_service import DeliveryService
from config.settings import settings
from repositories.user_repository import UserRepository
from utils.action_logger import ActionLogger

class CancelButton(Button):
    def __init__(self, delivery_id: int, user_id: int, bank_service: BankService, user_repo: UserRepository):
        super().__init__(label="🚫 Annuler", style=discord.ButtonStyle.red, custom_id=f"cancel_{delivery_id}")
        self.delivery_id = delivery_id
        self.user_id = user_id
        self.bank_service = bank_service
        self.user_repo = user_repo
        self.delivery_service = DeliveryService()
        self.logger = ActionLogger()

    async def callback(self, interaction: Interaction):
        delivery = self.delivery_service.get_delivery(self.delivery_id)
        if not delivery or delivery.get('is_cancelled', False):
            await interaction.response.send_message("❌ Livraison introuvable ou déjà annulée.", ephemeral=True)
            return

        self.delivery_service.cancel_delivery(self.delivery_id)
        user = self.user_repo.get_user(self.user_id)
        if not user:
            await interaction.response.send_message("❌ Utilisateur introuvable.", ephemeral=True)
            return

        new_balance = await self.bank_service.get_user_balance(self.user_id) + delivery['total_cost']
        success, message = await send_scum_command(
            f"#SetCurrencyBalance Normal {new_balance} {user['steam_id']}",
            self.user_id
        )

        self.logger.log_action(
            self.user_id, "delivery_cancelled",
            f"ID:{self.delivery_id}", "success",
            f"Remboursement: {delivery['total_cost']}"
        )

        await interaction.response.send_message(
            f"✅ Livraison annulée. {delivery['total_cost']} recrédités (solde: {new_balance}).",
            ephemeral=True
        )

        try:
            embed = interaction.message.embeds[0]
            embed.title = "🚫 Livraison annulée"
            embed.description = f"Remboursement de {delivery['total_cost']} effectué."
            embed.color = discord.Color.red()
            await interaction.message.edit(embed=embed, view=None)
        except Exception as e:
            print(f"Erreur mise à jour message: {e}")

class CheckDeliveryButton(Button):
    def __init__(self):
        super().__init__(label="🔍 Voir livraisons", style=discord.ButtonStyle.gray)

    async def callback(self, interaction: Interaction):
        if not any(role.id == settings.discord_role_garagiste for role in interaction.user.roles):
            await interaction.response.send_message("❌ Rôle admin requis.", ephemeral=True)
            return

        delivery_service = DeliveryService()
        active_deliveries = delivery_service.get_active_deliveries()

        if not active_deliveries:
            await interaction.response.send_message("Aucune livraison active.", ephemeral=True)
            return

        embed = Embed(title="📦 Livraisons actives", color=discord.Color.blue())
        for delivery in active_deliveries:
            try:
                ends_at_str = str(delivery['ends_at']).split('.')[0]
                ends_at = datetime.strptime(ends_at_str, "%Y-%m-%d %H:%M:%S")
                remaining = max(0, (ends_at - datetime.now()).total_seconds() / 60)

                embed.add_field(
                    name=f"ID: {delivery['id']}",
                    value=(
                        f"**Utilisateur**: <@{delivery['user_id']}>\n"
                        f"**Item**: {delivery['item']} x{delivery['quantity']}\n"
                        f"**Position**: {delivery['delivery_location']}\n"
                        f"**Temps restant**: {int(remaining)} min\n"
                        f"**Coût**: {delivery['total_cost']}€"
                    ),
                    inline=False
                )
            except Exception as e:
                print(f"Erreur affichage livraison {delivery.get('id')}: {e}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

class ItemSelectView(View):
    def __init__(self, bank_service: BankService, user_repo: UserRepository, user_id: int):
        super().__init__(timeout=180)
        self.bank_service = bank_service
        self.user_repo = user_repo
        self.user_id = user_id
        self.select = Select(
            placeholder="Sélectionnez un item",
            options=[
                discord.SelectOption(label="Kit de réparation voiture", value="Car_Repair_Kit"),
                discord.SelectOption(label="Bidon d'essence", value="Gasoline_Canister")
            ]
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: Interaction):
        await interaction.response.send_modal(
            QuantityModal(
                self.select.values[0],
                self.bank_service,
                self.user_repo,
                interaction,
                self.user_id
            )
        )

class QuantityModal(Modal):
    def __init__(self, item: str, bank_service: BankService, user_repo: UserRepository, interaction: Interaction, user_id: int):
        super().__init__(title=f"Quantité pour {item}")
        self.item = item
        self.bank_service = bank_service
        self.user_repo = user_repo
        self.interaction = interaction
        self.user_id = user_id
        self.quantity = TextInput(
            label="Quantité (1-20)",
            placeholder="Ex: 5",
            min_length=1,
            max_length=2
        )
        self.add_item(self.quantity)

    async def on_submit(self, interaction: Interaction):
        try:
            quantity = int(self.quantity.value)
            if not 1 <= quantity <= 20:
                await interaction.response.send_message("❌ La quantité doit être entre 1 et 20.", ephemeral=True)
                return

            await interaction.response.send_message("✅ Commande enregistrée ! Vérifiez vos MP.", ephemeral=True)
            asyncio.create_task(self.process_delivery(interaction, quantity))
        except ValueError:
            await interaction.response.send_message("❌ Veuillez entrer un nombre valide.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {str(e)}", ephemeral=True)

    async def process_delivery(self, interaction: Interaction, quantity: int):
        try:
            total_cost = quantity * 1000
            user = self.user_repo.get_user(self.user_id)

            # Vérifie que l'utilisateur existe et a un SteamID
            if not user or 'steam_id' not in user or not user['steam_id']:
                await interaction.user.send("❌ SteamID non lié.")
                return

            # Récupère le solde
            balance = await self.bank_service.get_user_balance(self.user_id)
            if balance < 0:
                await interaction.user.send("❌ Erreur de connexion à la base SCUM.")
                return
            if balance < total_cost:
                await interaction.user.send(f"❌ Solde insuffisant (vous avez {balance}€).")
                return

            # Retire l'argent
            new_balance = balance - total_cost
            success, message = await self.bank_service.withdraw(self.user_id, total_cost)
            if not success:
                await interaction.user.send(f"❌ {message}")
                return

            # Envoie la commande SCUM pour mettre à jour le solde
            success, message = await send_scum_command(
                f"#SetCurrencyBalance Normal {new_balance} {user['steam_id']}",  # Accès correct au steam_id
                self.user_id
            )
            if not success:
                await interaction.user.send(f"⚠️ {message} (mise à jour solde)")
                return

            delivery_location = random.choice(list(DELIVERY_POSITIONS.keys()))
            coords = DELIVERY_POSITIONS[delivery_location]
            delivery_service = DeliveryService()
            delivery_id = delivery_service.create_delivery(
                self.user_id, self.item, quantity, total_cost,
                delivery_location, coords, user['steam_id']
            )

            embed = Embed(
                title="📦 Livraison en cours",
                description="⏳ Temps restant: **20m 00s**",
                color=discord.Color.blue()
            )
            embed.add_field(name="📍 Position", value=delivery_location)
            embed.add_field(name="💰 Coût", value=f"{total_cost}€ (solde: {new_balance}€)")
            embed.add_field(name="📦 Item", value=f"{self.item} x{quantity}")
            embed.set_footer(text=f"ID: {delivery_id}")

            timer_message = await interaction.user.send(
                embed=embed,
                view=View().add_item(CancelButton(delivery_id, self.user_id, self.bank_service, self.user_repo))
            )

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
                    success, message = await send_scum_command(
                        f"#announce Livraison pour {interaction.user.name} à {delivery_location} dans 5 minutes!",
                        self.user_id
                    )
                    if not success:
                        await interaction.user.send(f"⚠️ {message} (annonce)")

                    await asyncio.sleep(5*60)

                    success, message = await send_scum_command(
                        f"#TeleportTo {coords[0]} {coords[1]} {coords[2]}",
                        self.user_id
                    )
                    if not success:
                        await interaction.user.send(f"⚠️ {message} (téléportation)")
                        return

                    for i in range(quantity):
                        success, message = await send_scum_command(
                            f"#SpawnItem {self.item} 1",
                            self.user_id
                        )
                        if not success:
                            await interaction.user.send(f"⚠️ {message} (spawn {i+1}/{quantity})")
                        await asyncio.sleep(1.5)

                    embed.description = "🚛 Livraison effectuée!"
                    embed.color = discord.Color.green()
                    await timer_message.edit(embed=embed, view=None)
                    delivery_service.complete_delivery(delivery_id)

            asyncio.create_task(update_timer())

        except Exception as e:
            await interaction.user.send(f"❌ Erreur: {str(e)}")
            import traceback
            print(traceback.format_exc())

class RavitaillementGarageButton(Button):
    def __init__(self):
        super().__init__(
            label="🚔 Ravitaillement Garage",
            style=discord.ButtonStyle.blurple,
            custom_id="ravitaillement_garage"
        )
        self.bank_service = BankService()
        self.user_repo = UserRepository()

    async def callback(self, interaction: Interaction):
        if not any(role.id == settings.discord_role_garagiste for role in interaction.user.roles):
            await interaction.response.send_message("❌ Rôle 'Garagiste' requis.", ephemeral=True)
            return

        user = self.user_repo.get_user(interaction.user.id)
        if not user or not user.get('steam_id'):
            await interaction.response.send_message(
                "❌ Vous devez d'abord lier votre SteamID.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "📦 Sélectionnez un item:",
            view=ItemSelectView(self.bank_service, self.user_repo, interaction.user.id),
            ephemeral=True
        )

class AdminDeliveryButton(Button):
    def __init__(self):
        super().__init__(
            label="📋 Admin: Livraisons",
            style=discord.ButtonStyle.gray,
            custom_id="admin_deliveries"
        )

    async def callback(self, interaction: Interaction):
        if not any(role.id == settings.discord_role_garagiste for role in interaction.user.roles):
            await interaction.response.send_message("❌ Rôle admin requis.", ephemeral=True)
            return

        await interaction.response.send_message(
            "Livraisons actives:",
            view=View().add_item(CheckDeliveryButton()),
            ephemeral=True
        )

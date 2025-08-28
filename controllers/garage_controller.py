from datetime import datetime, timedelta
import discord
import random
import asyncio
from discord.ui import Button, Select, View, Modal, TextInput
from discord import Interaction, Embed
from repositories.scum_repository import logger
from services.bank_service import BankService
from services.scum_service import send_scum_command
from services.delivery_service import DeliveryService
from config.settings import settings
from repositories.user_repository import UserRepository
from utils.action_logger import ActionLogger
from config.constants import DELIVERY_POSITIONS, ITEM_PRICES, INSTANT_VEHICLE_POSITION


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
        await interaction.response.defer(ephemeral=True)

        try:
            delivery = self.delivery_service.get_delivery(self.delivery_id)
            if not delivery or delivery.get('is_cancelled', False):
                await interaction.followup.send("❌ Livraison introuvable ou déjà annulée.", ephemeral=True)
                return

            self.delivery_service.cancel_delivery(self.delivery_id)
            user = self.user_repo.get_user(self.user_id)
            if not user:
                await interaction.followup.send("❌ Utilisateur introuvable.", ephemeral=True)
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

            await interaction.followup.send(
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

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)

class CheckDeliveryButton(Button):
    def __init__(self):
        super().__init__(label="🔍 Voir livraisons", style=discord.ButtonStyle.gray)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            if not any(role.id == settings.discord_role_garagiste for role in interaction.user.roles):
                await interaction.followup.send("❌ Rôle admin requis.", ephemeral=True)
                return

            delivery_service = DeliveryService()
            active_deliveries = delivery_service.get_active_deliveries()

            if not active_deliveries:
                await interaction.followup.send("Aucune livraison active.", ephemeral=True)
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

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)

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
        await interaction.response.defer(ephemeral=True)

        try:
            quantity = int(self.quantity.value)
            if not 1 <= quantity <= 20:
                await interaction.followup.send("❌ La quantité doit être entre 1 et 20.", ephemeral=True)
                return

            item_price = ITEM_PRICES.get(self.item, 0)
            total_cost = quantity * item_price

            # Message immédiat + traitement en arrière-plan
            await interaction.followup.send(
                "✅ Commande reçue! Préparation en cours (vérifiez vos MP pour le suivi).",
                ephemeral=True
            )

            # Lance le traitement en tâche séparée
            asyncio.create_task(self._process_delivery(interaction, quantity, total_cost))

        except ValueError:
            await interaction.followup.send("❌ Veuillez entrer un nombre valide.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur initiale: {str(e)}", ephemeral=True)

    async def _process_delivery(self, interaction: Interaction, quantity: int, total_cost: int):
        """Méthode de traitement en arrière-plan avec gestion des erreurs"""
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
                description="⏳ Temps restant: **20m 00s**",
                color=discord.Color.blue()
            )
            embed.add_field(name="📍 Position", value=delivery_location)
            embed.add_field(name="💰 Coût", value=f"{total_cost}€ (solde: {new_balance}€)")
            embed.add_field(name="📦 Item", value=f"{self.item} x{quantity}")
            embed.set_footer(text=f"ID: {delivery_id}")

            timer_message = await interaction.user.send(embed=embed)

            # Configuration du timer
            ends_at = datetime.now() + timedelta(minutes=20)
            delivery_service.update_ends_at(delivery_id, ends_at.strftime("%Y-%m-%d %H:%M:%S"))

            # Lancement du timer en tâche séparée
            asyncio.create_task(self._update_timer(
                delivery_service, delivery_id, timer_message, embed,
                interaction.user, coords, quantity, delivery_location
            ))

        except Exception as e:
            await interaction.user.send(f"❌ Erreur critique: {str(e)}")
            logger.error(f"Erreur process_delivery: {str(e)}")

    async def _update_timer(self, delivery_service, delivery_id, timer_message, embed,
                           user, coords, quantity, delivery_location):
        """Gère le timer de la livraison en arrière-plan"""
        try:
            while True:
                delivery = delivery_service.get_delivery(delivery_id)
                if not delivery or delivery.get('is_cancelled', False) or delivery.get('is_completed', False):
                    return

                ends_at_str = str(delivery['ends_at']).split('.')[0]
                ends_at = datetime.strptime(ends_at_str, "%Y-%m-%d %H:%M:%S")
                remaining = (ends_at - datetime.now()).total_seconds()

                if remaining <= 0:
                    break

                embed.description = f"⏳ Temps restant: {int(remaining//60)}m {int(remaining%60)}s"
                await timer_message.edit(embed=embed)
                await asyncio.sleep(30)

            # Annonce à 5 minutes
            if not delivery_service.get_delivery(delivery_id).get('is_cancelled', False):
                success, message = await send_scum_command(
                    f"#announce Livraison pour {self.interaction.user.name} à {delivery_location} dans 5 minutes!",
                    self.user_id
                )
                if not success:
                    await user.send(f"⚠️ {message} (annonce)")

                await asyncio.sleep(5*60)

                # Livraison finale
                success, message = await send_scum_command(
                    f"#TeleportTo {coords[0]} {coords[1]} {coords[2]}",
                    self.user_id
                )
                if not success:
                    await user.send(f"⚠️ {message} (téléportation)")
                    return

                for i in range(quantity):
                    success, message = await send_scum_command(
                        f"#SpawnItem {self.item} 1",
                        self.user_id
                    )
                    if not success:
                        await user.send(f"⚠️ {message} (spawn {i+1}/{quantity})")
                    await asyncio.sleep(1.5)

                embed.description = "🚛 Livraison effectuée!"
                embed.color = discord.Color.green()
                await timer_message.edit(embed=embed, view=None)
                delivery_service.complete_delivery(delivery_id)

        except Exception as e:
            await user.send(f"❌ Erreur dans le timer: {str(e)}")
            logger.error(f"Erreur timer: {str(e)}")

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
        await interaction.response.defer(ephemeral=True)

        try:
            if not any(role.id == settings.discord_role_garagiste for role in interaction.user.roles):
                await interaction.followup.send("❌ Rôle 'Garagiste' requis.", ephemeral=True)
                return

            user = self.user_repo.get_user(interaction.user.id)
            if not user or 'steam_id' not in user or not user['steam_id']:
                await interaction.followup.send(
                    "❌ Vous devez d'abord lier votre SteamID.",
                    ephemeral=True
                )
                return

            await interaction.followup.send(
                "📦 Sélectionnez un item:",
                view=ItemSelectView(self.bank_service, self.user_repo, interaction.user.id),
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)

class AdminDeliveryButton(Button):
    def __init__(self):
        super().__init__(
            label="📋 Admin: Livraisons",
            style=discord.ButtonStyle.gray,
            custom_id="admin_deliveries"
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            if not any(role.id == settings.discord_role_garagiste for role in interaction.user.roles):
                await interaction.followup.send("❌ Rôle admin requis.", ephemeral=True)
                return

            await interaction.followup.send(
                "Livraisons actives:",
                view=View().add_item(CheckDeliveryButton()),
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)

class InstantVehicleSelectView(View):
    def __init__(self, bank_service: BankService, user_repo: UserRepository, user_id: int):
        super().__init__(timeout=180)
        self.bank_service = bank_service
        self.user_repo = user_repo
        self.user_id = user_id
        self.select = Select(
            placeholder="Sélectionnez un véhicule",
            options=[
                discord.SelectOption(label="BP_Cruiser_B (20 000€)", value="BP_Cruiser_B"),
                discord.SelectOption(label="BP_Dirtbike_A (30 000€)", value="BP_Dirtbike_A"),
            ]
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: Interaction):
        await interaction.response.send_modal(
            InstantVehicleConfirmModal(
                self.select.values[0],
                self.bank_service,
                self.user_repo,
                interaction,
                self.user_id
            )
        )

class InstantVehicleConfirmModal(Modal):
    def __init__(self, vehicle: str, bank_service: BankService, user_repo: UserRepository, interaction: Interaction, user_id: int):
        super().__init__(title=f"Confirmation: {vehicle}")
        self.vehicle = vehicle
        self.bank_service = bank_service
        self.user_repo = user_repo
        self.interaction = interaction
        self.user_id = user_id
        self.confirm = TextInput(
            label="Tapez 'OUI' pour confirmer l'achat",
            placeholder="OUI",
            required=True
        )
        self.add_item(self.confirm)

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        if self.confirm.value.upper() != "OUI":
            await interaction.followup.send("❌ Annulé.", ephemeral=True)
            return
        try:
            vehicle_price = ITEM_PRICES.get(self.vehicle, 0)
            user = self.user_repo.get_user(self.user_id)
            if not user or 'steam_id' not in user:
                await interaction.followup.send("❌ SteamID non lié.", ephemeral=True)
                return
            # Vérification du solde
            balance = await self.bank_service.get_user_balance(self.user_id)
            if balance < 0:
                await interaction.followup.send("❌ Erreur de connexion à la base SCUM.", ephemeral=True)
                return
            # Correction : extraire la valeur du solde si c'est un tuple
            balance_value = balance[0] if isinstance(balance, tuple) else balance
            if balance_value < vehicle_price:
                await interaction.followup.send(f"❌ Solde insuffisant ({balance_value}€).", ephemeral=True)
                return
            # Retrait des fonds
            new_balance = balance_value - vehicle_price
            success, _ = await self.bank_service.withdraw(self.user_id, vehicle_price)
            if not success:
                await interaction.followup.send("❌ Erreur lors du retrait.", ephemeral=True)
                return
            # Mise à jour du solde dans SCUM
            success, message = await send_scum_command(
                f"#SetCurrencyBalance Normal {new_balance} {user['steam_id']}",
                self.user_id
            )
            if not success:
                await interaction.followup.send(f"⚠️ {message}", ephemeral=True)
                return
            # Téléportation et spawn
            await interaction.followup.send("🔄 Téléportation et spawn en cours...", ephemeral=True)
            success, message = await send_scum_command(
                f"#TeleportTo {INSTANT_VEHICLE_POSITION[0]} {INSTANT_VEHICLE_POSITION[1]} {INSTANT_VEHICLE_POSITION[2]}",
                self.user_id
            )
            if not success:
                await interaction.followup.send(f"❌ Échec de la téléportation: {message}. Contactez un administrateur.",
                                                ephemeral=True)
                return
            await asyncio.sleep(2)  # Attendre la téléportation
            success, message = await send_scum_command(
                f"#SpawnVehicle {self.vehicle}",
                self.user_id
            )
            if not success:
                await interaction.followup.send(f"❌ Échec du spawn: {message}. Contactez un administrateur.",
                                                ephemeral=True)
                return
            await interaction.followup.send(f"✅ Véhicule {self.vehicle} spawné avec succès !", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}. Contactez un administrateur.", ephemeral=True)

class InstantVehicleSpawnButton(Button):
    def __init__(self):
        super().__init__(
            label="🚗 Spawn Véhicule Instantané",
            style=discord.ButtonStyle.success,
            custom_id="instant_vehicle_spawn"
        )
        self.bank_service = BankService()
        self.user_repo = UserRepository()

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            if not any(role.id == settings.discord_role_garagiste for role in interaction.user.roles):
                await interaction.followup.send("❌ Rôle 'Garagiste' requis.", ephemeral=True)
                return
            user = self.user_repo.get_user(interaction.user.id)
            if not user or 'steam_id' not in user or not user['steam_id']:
                await interaction.followup.send("❌ Vous devez d'abord lier votre SteamID.", ephemeral=True)
                return
            await interaction.followup.send(
                "🚗 Sélectionnez un véhicule:",
                view=InstantVehicleSelectView(self.bank_service, self.user_repo, interaction.user.id),
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)

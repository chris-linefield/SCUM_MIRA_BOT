import asyncio

from config import INSTANT_VEHICLE_POSITION, MERCHANT_DELIVERY_POSITIONS
from repositories.scum_repository import get_bank_balance, update_bank_balance
from services.game_client import GameClient
from utils.logger import logger

class ScumService:
    @staticmethod
    async def buy_item(user_steam_id: str, item_id: str, count: int, price: int, merchant_type: str) -> bool:
        balance = get_bank_balance(user_steam_id)
        total_price = price * count
        if balance < total_price:
            logger.error(f"Solde insuffisant pour {user_steam_id}.")
            return False

        new_balance = balance - total_price
        set_balance_command = f"#SetCurrencyBalance Normal {new_balance} {user_steam_id}"
        success, message = await GameClient.send_command(set_balance_command)
        if not success:
            logger.error(f"Erreur lors de la mise à jour du solde pour {user_steam_id}: {message}")
            return False

        if not update_bank_balance(user_steam_id, new_balance):
            logger.error(f"Erreur lors de la mise à jour du solde local pour {user_steam_id}.")
            return False

        # Téléportation avant le spawn de l'item
        x, y, z = MERCHANT_DELIVERY_POSITIONS[merchant_type]
        teleport_command = f"#Teleport {x} {y} {z}"
        success, _ = await GameClient.send_command(teleport_command)
        if not success:
            logger.error(f"Erreur lors de la téléportation pour le spawn de l'item.")
            return False

        await asyncio.sleep(10)  # Attendre 10 secondes pour le chargement de la zone

        spawn_command = f"#SpawnItem {item_id} {count}"
        success, _ = await GameClient.send_command(spawn_command)
        if not success:
            logger.error(f"Erreur lors du spawn de l'item {item_id}.")
            return False

        return True

    @staticmethod
    async def buy_vehicle(user_steam_id: str, vehicle_id: str, price: int) -> bool:
        balance = get_bank_balance(user_steam_id)
        if balance < price:
            logger.error(f"Solde insuffisant pour {user_steam_id}.")
            return False

        new_balance = balance - price
        set_balance_command = f"#SetCurrencyBalance Normal {new_balance} {user_steam_id}"
        success, message = await GameClient.send_command(set_balance_command)
        if not success:
            logger.error(f"Erreur lors de la mise à jour du solde pour {user_steam_id}: {message}")
            return False

        if not update_bank_balance(user_steam_id, new_balance):
            logger.error(f"Erreur lors de la mise à jour du solde local pour {user_steam_id}.")
            return False

        # Téléportation avant le spawn du véhicule
        x, y, z = INSTANT_VEHICLE_POSITION
        teleport_command = f"#Teleport {x} {y} {z}"
        success, _ = await GameClient.send_command(teleport_command)
        if not success:
            logger.error(f"Erreur lors de la téléportation pour le spawn du véhicule.")
            return False

        await asyncio.sleep(10)  # Attendre 10 secondes pour le chargement de la zone

        spawn_command = f"#SpawnVehicle {vehicle_id}"
        success, _ = await GameClient.send_command(spawn_command)
        if not success:
            logger.error(f"Erreur lors du spawn du véhicule {vehicle_id}.")
            return False

        return True

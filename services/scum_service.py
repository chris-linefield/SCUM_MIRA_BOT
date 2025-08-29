from repositories.scum_repository import get_bank_balance, update_bank_balance
from services.game_client import GameClient
from utils.logger import logger

class ScumService:
    @staticmethod
    async def buy_item(user_steam_id: str, item_id: str, count: int, price: int) -> bool:
        balance = get_bank_balance(user_steam_id)
        total_price = price * count
        if balance < total_price:
            logger.error(f"Solde insuffisant pour {user_steam_id}.")
            return False

        new_balance = balance - total_price
        if not update_bank_balance(user_steam_id, new_balance):
            logger.error(f"Erreur lors de la mise à jour du solde pour {user_steam_id}.")
            return False

        return await GameClient.spawn_item(item_id, count)

    @staticmethod
    async def buy_vehicle(user_steam_id: str, vehicle_id: str, price: int) -> bool:
        balance = get_bank_balance(user_steam_id)
        if balance < price:
            logger.error(f"Solde insuffisant pour {user_steam_id}.")
            return False

        new_balance = balance - price
        if not update_bank_balance(user_steam_id, new_balance):
            logger.error(f"Erreur lors de la mise à jour du solde pour {user_steam_id}.")
            return False

        return await GameClient.spawn_vehicle(vehicle_id)
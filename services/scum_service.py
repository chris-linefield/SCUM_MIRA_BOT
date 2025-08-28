from repositories.scum_repository import get_user_balance
from services.game_client import GameClient
from utils.logger import logger

class ScumService:
    @staticmethod
    def buy_item(user_steam_id: str, item_id: str, count: int, price: int) -> bool:
        balance = get_user_balance(user_steam_id)
        if balance < price * count:
            logger.error(f"Solde insuffisant pour {user_steam_id}.")
            return False
        return GameClient.spawn_item(item_id, count)

    @staticmethod
    def buy_vehicle(user_steam_id: str, vehicle_id: str, price: int) -> bool:
        balance = get_user_balance(user_steam_id)
        if balance < price:
            logger.error(f"Solde insuffisant pour {user_steam_id}.")
            return False
        return GameClient.spawn_vehicle(vehicle_id)

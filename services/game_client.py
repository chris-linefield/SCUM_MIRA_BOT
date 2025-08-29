from typing import Tuple

from services.scum_manager import send_scum_command
from utils.logger import logger

class GameClient:
    @staticmethod
    async def spawn_item(item_id: str, count: int = 1) -> bool:
        command = f"#SpawnItem {item_id} {count}"
        success, message = await send_scum_command(command)
        if success:
            logger.info(f"Item {item_id} x{count} spawné.")
            return True
        else:
            logger.error(f"Erreur lors du spawn de l'item: {message}")
            return False

    @staticmethod
    async def spawn_vehicle(vehicle_id: str) -> bool:
        command = f"#SpawnVehicle {vehicle_id}"
        success, message = await send_scum_command(command)
        if success:
            logger.info(f"Véhicule {vehicle_id} spawné.")
            return True
        else:
            logger.error(f"Erreur lors du spawn du véhicule: {message}")
            return False

    @staticmethod
    async def announce(message: str) -> Tuple[bool, str]:
        command = f"#Announce {message}"
        success, message = await send_scum_command(command)
        if success:
            logger.info(f"Annonce envoyée: {message}")
            return True, message
        else:
            logger.error(f"Erreur lors de l'envoi de l'annonce: {message}")
            return False, message

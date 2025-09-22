import asyncio
import random
from datetime import datetime, timedelta
from typing import Tuple
from repositories.db_manager import add_delivery, get_pending_deliveries, update_delivery_status
from config.constants import MERCHANT_DELIVERY_POSITIONS, DELIVERY_TIME, PACK_ITEMS
from services.scum_manager import send_scum_command
from utils.logger import logger

async def schedule_delivery(bot, user_discord_id: int, user_steam_id: str, item_id: str, count: int, merchant_type: str, is_pack: bool = False) -> bool:
    """Planifie une livraison (item ou pack)."""
    try:
        delivery_position = MERCHANT_DELIVERY_POSITIONS[merchant_type]
        delivery_time = (datetime.now() + timedelta(minutes=DELIVERY_TIME)).strftime("%Y-%m-%d %H:%M:%S")
        if not add_delivery(user_discord_id, user_steam_id, item_id, count, merchant_type, delivery_time, is_pack):
            logger.error(f"Erreur lors de l'ajout de la livraison pour {user_steam_id}.")
            return False
        logger.info(f"Livraison planifiée pour {user_steam_id}: {item_id} x{count} à {merchant_type}.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la planification de la livraison: {e}")
        return False

async def check_pending_deliveries(bot):
    """Vérifie et traite les livraisons en cours."""
    while True:
        try:
            await asyncio.sleep(60)  # Vérifier toutes les minutes
            pending = get_pending_deliveries()
            for delivery in pending:
                delivery_id, user_id, steam_id, item_id, quantity, merchant_type, delivery_time_str, is_pack_str = delivery
                is_pack = is_pack_str == "1"  # Convertir depuis la base de données
                delivery_time = datetime.strptime(delivery_time_str, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                time_until_delivery = (delivery_time - now).total_seconds()
                if time_until_delivery <= 0:
                    await execute_delivery(delivery_id, steam_id, item_id, quantity, merchant_type, is_pack)
        except Exception as e:
            logger.error(f"Erreur dans check_pending_deliveries: {e}")
            await asyncio.sleep(60)

async def execute_delivery(delivery_id: int, steam_id: str, item_id: str, quantity: int, merchant_type: str, is_pack: bool):
    """Exécute une livraison (item ou pack)."""
    if is_pack:
        for pack_item in PACK_ITEMS[item_id]:
            await teleport_and_spawn(delivery_id, steam_id, pack_item, quantity, merchant_type)
            await asyncio.sleep(2)  # Délai entre chaque item du pack
    else:
        await teleport_and_spawn(delivery_id, steam_id, item_id, quantity, merchant_type)

async def teleport_and_spawn(delivery_id: int, steam_id: str, item_id: str, quantity: int, merchant_type: str):
    """Téléporte et fait spawner les items."""
    x, y, z = MERCHANT_DELIVERY_POSITIONS[merchant_type]
    teleport_command = f"#Teleport {x} {y} {z}"
    success, _ = await send_scum_command(teleport_command)
    if success:
        logger.info(f"Téléportation au {merchant_type} réussie.")
        await asyncio.sleep(10)  # Attendre 10 secondes pour le chargement de la zone
        spawn_command = f"#SpawnItem {item_id} {quantity}"
        success, _ = await send_scum_command(spawn_command)
        if success:
            logger.info(f"Spawn de {item_id} x{quantity} réussi au {merchant_type}.")
            update_delivery_status(delivery_id, "delivered")
        else:
            logger.error(f"Erreur lors du spawn de {item_id} x{quantity} au {merchant_type}.")
    else:
        logger.error(f"Erreur lors de la téléportation au {merchant_type}.")
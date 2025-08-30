import asyncio
import random
from datetime import datetime, timedelta
from typing import Tuple
from repositories.db_manager import add_delivery, get_pending_deliveries, update_delivery_status
from config.constants import DELIVERY_POSITIONS, DELIVERY_TIME
from repositories.scum_repository import get_bank_balance
from services.scum_manager import send_scum_command
from utils.logger import logger

async def schedule_delivery(bot, user_discord_id: int, user_steam_id: str, item_id: str, count: int) -> bool:
    """Planifie une livraison."""
    try:
        delivery_position = random.choice(list(DELIVERY_POSITIONS.keys()))
        delivery_time = (datetime.now() + timedelta(minutes=DELIVERY_TIME)).strftime("%Y-%m-%d %H:%M:%S")

        if not add_delivery(user_discord_id, user_steam_id, item_id, count, delivery_position, delivery_time):
            logger.error(f"Erreur lors de l'ajout de la livraison pour {user_steam_id}.")
            return False

        logger.info(f"Livraison planifiée pour {user_steam_id}: {item_id} x{count} à {delivery_position}.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la planification de la livraison: {e}")
        return False

async def check_pending_deliveries(bot):
    """Vérifie et traite les livraisons en cours."""
    while True:
        try:
            pending_deliveries = get_pending_deliveries()
            for delivery in pending_deliveries:
                delivery_id, user_id, steam_id, item_id, quantity, delivery_position, delivery_time, _ = delivery
                await process_delivery(bot, delivery_id, user_id, steam_id, item_id, quantity, delivery_position, delivery_time)
            await asyncio.sleep(60)  # Vérifier toutes les minutes
        except Exception as e:
            logger.error(f"Erreur dans check_pending_deliveries: {e}")
            await asyncio.sleep(60)

async def process_delivery(bot, delivery_id: int, user_id: int, steam_id: str, item_id: str, quantity: int, delivery_position: str, delivery_time: str):
    """Traite une livraison en cours."""
    from datetime import datetime
    delivery_time = datetime.strptime(delivery_time, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    time_until_delivery = (delivery_time - now).total_seconds()

    if time_until_delivery <= 0:
        # Vérifier le solde avant la livraison
        balance = get_bank_balance(steam_id)
        if balance is None:
            logger.error(f"Erreur lors de la récupération du solde pour {steam_id}.")
            return

        # Exécuter la livraison
        await execute_delivery(delivery_id, steam_id, item_id, quantity, delivery_position)
    elif time_until_delivery <= 300:  # 5 minutes avant la livraison
        if time_until_delivery <= 60:  # 1 minute avant la livraison
            await announce_delivery(delivery_position)
            await asyncio.sleep(60)  # Attendre 1 minute
            await teleport_and_spawn(delivery_id, steam_id, item_id, quantity, delivery_position)
        else:
            await announce_delivery_soon(bot, delivery_position, time_until_delivery)

async def announce_delivery_soon(bot, delivery_position: str, time_until_delivery: float):
    """Annonce une livraison imminente."""
    minutes = int(time_until_delivery / 60)
    message = f"#Announce Livraison M.I.R.A dans {minutes} minutes à {delivery_position} !"
    success, _ = await send_scum_command(message)
    if success:
        logger.info(f"Annonce de livraison dans {minutes} minutes envoyée pour {delivery_position}.")
    else:
        logger.error(f"Erreur lors de l'envoi de l'annonce de livraison pour {delivery_position}.")

async def announce_delivery(delivery_position: str):
    """Annonce une livraison en cours."""
    message = f"#Announce Livraison M.I.R.A en cours à {delivery_position} !"
    success, _ = await send_scum_command(message)
    if success:
        logger.info(f"Annonce de livraison en cours envoyée pour {delivery_position}.")
    else:
        logger.error(f"Erreur lors de l'envoi de l'annonce de livraison pour {delivery_position}.")

async def teleport_and_spawn(delivery_id: int, steam_id: str, item_id: str, quantity: int, delivery_position: str):
    """Téléporte et fait spawner les items."""
    x, y, z = DELIVERY_POSITIONS[delivery_position]
    teleport_command = f"#Teleport {x} {y} {z}"
    success, _ = await send_scum_command(teleport_command)
    if success:
        logger.info(f"Téléportation à {delivery_position} réussie.")
        await asyncio.sleep(10)  # Attendre 10 secondes pour le chargement de la zone
        spawn_command = f"#SpawnItem {item_id} {quantity}"
        success, _ = await send_scum_command(spawn_command)
        if success:
            logger.info(f"Spawn de {item_id} x{quantity} réussi à {delivery_position}.")
            update_delivery_status(delivery_id, "delivered")
        else:
            logger.error(f"Erreur lors du spawn de {item_id} x{quantity} à {delivery_position}.")
    else:
        logger.error(f"Erreur lors de la téléportation à {delivery_position}.")

async def execute_delivery(delivery_id: int, steam_id: str, item_id: str, quantity: int, delivery_position: str):
    """Exécute une livraison."""
    await teleport_and_spawn(delivery_id, steam_id, item_id, quantity, delivery_position)

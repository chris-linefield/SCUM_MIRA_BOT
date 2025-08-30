import sqlite3
from config import settings
from utils.logger import logger

def initialize_delivery_db():
    conn = sqlite3.connect(settings.local_db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                steam_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                delivery_position TEXT NOT NULL,
                delivery_time DATETIME NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        conn.commit()
        logger.info("Table pending_deliveries initialisée avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la table pending_deliveries: {e}")
    finally:
        conn.close()

def add_delivery(user_id: int, steam_id: str, item_id: str, quantity: int, delivery_position: str, delivery_time: str) -> bool:
    conn = sqlite3.connect(settings.local_db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO pending_deliveries
            (user_id, steam_id, item_id, quantity, delivery_position, delivery_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, steam_id, item_id, quantity, delivery_position, delivery_time)
        )
        conn.commit()
        logger.info(f"Livraison ajoutée pour {steam_id}: {item_id} x{quantity} à {delivery_position}.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de la livraison: {e}")
        return False
    finally:
        conn.close()

def get_pending_deliveries() -> list:
    conn = sqlite3.connect(settings.local_db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pending_deliveries WHERE status = 'pending'")
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des livraisons en cours: {e}")
        return []
    finally:
        conn.close()

def update_delivery_status(delivery_id: int, status: str) -> bool:
    conn = sqlite3.connect(settings.local_db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE pending_deliveries SET status = ? WHERE id = ?",
            (status, delivery_id)
        )
        conn.commit()
        logger.info(f"Statut de la livraison {delivery_id} mis à jour en {status}.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du statut de la livraison: {e}")
        return False
    finally:
        conn.close()

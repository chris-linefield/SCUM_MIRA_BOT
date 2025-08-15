import sqlite3
from datetime import datetime, timedelta
from config.settings import settings
from utils.logger import logger

class DeliveryService:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(settings.local_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS active_deliveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    item TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_cost INTEGER NOT NULL,
                    delivery_location TEXT NOT NULL,
                    coords_x REAL NOT NULL,
                    coords_y REAL NOT NULL,
                    coords_z REAL NOT NULL,
                    steam_id TEXT NOT NULL,
                    starts_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ends_at DATETIME NOT NULL,
                    is_cancelled BOOLEAN DEFAULT FALSE,
                    is_completed BOOLEAN DEFAULT FALSE
                )
            ''')
            conn.commit()

    def create_delivery(self, user_id: int, item: str, quantity: int, total_cost: int,
                       delivery_location: str, coords: tuple, steam_id: str) -> int:
        ends_at = datetime.now() + timedelta(minutes=20)
        with sqlite3.connect(settings.local_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO active_deliveries
                (user_id, item, quantity, total_cost, delivery_location,
                 coords_x, coords_y, coords_z, steam_id, ends_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, item, quantity, total_cost, delivery_location,
                  coords[0], coords[1], coords[2], steam_id, ends_at))
            conn.commit()
            return cursor.lastrowid

    def update_ends_at(self, delivery_id: int, ends_at: str) -> bool:
        try:
            with sqlite3.connect(settings.local_db_path) as conn:
                conn.execute('''
                    UPDATE active_deliveries
                    SET ends_at = ?
                    WHERE id = ?
                ''', (ends_at, delivery_id))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erreur mise à jour ends_at: {e}")
            return False

    def cancel_delivery(self, delivery_id: int) -> bool:
        with sqlite3.connect(settings.local_db_path) as conn:
            conn.execute('''
                UPDATE active_deliveries
                SET is_cancelled = TRUE,
                    ends_at = datetime('now')
                WHERE id = ?
            ''', (delivery_id,))
            conn.commit()
        return True

    def complete_delivery(self, delivery_id: int) -> bool:
        with sqlite3.connect(settings.local_db_path) as conn:
            conn.execute('''
                UPDATE active_deliveries
                SET is_completed = TRUE
                WHERE id = ?
            ''', (delivery_id,))
            conn.commit()
        return True

    def get_delivery(self, delivery_id: int) -> dict:
        with sqlite3.connect(settings.local_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM active_deliveries WHERE id = ?', (delivery_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_active_deliveries(self) -> list:
        with sqlite3.connect(settings.local_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM active_deliveries
                WHERE is_cancelled = FALSE
                AND is_completed = FALSE
                AND ends_at > datetime('now')
            ''')
            return [dict(row) for row in cursor.fetchall()]

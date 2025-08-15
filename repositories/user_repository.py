import sqlite3
from datetime import datetime

from config.settings import settings
from utils.logger import logger

class UserRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path or settings.local_db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    discord_id INTEGER PRIMARY KEY,
                    steam_id TEXT UNIQUE,
                    name TEXT,
                    age TEXT,
                    crime TEXT,
                    sentence TEXT,
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def is_user_registered(self, discord_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM users WHERE discord_id = ?', (discord_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Erreur vérification utilisateur: {e}")
            return False

    def link_steam_id(self, discord_id: int, steam_id: str, name: str = None,
                     age: str = None, crime: str = None, sentence: str = None) -> bool:
        try:
            if self.is_user_registered(discord_id):
                return False

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO users
                    (discord_id, steam_id, name, age, crime, sentence, registered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (discord_id, steam_id, name, age, crime, sentence, datetime.now()))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.error(f"SteamID {steam_id} déjà utilisé")
            return False
        except Exception as e:
            logger.error(f"Erreur lien SteamID: {e}")
            return False

    def get_user(self, discord_id: int) -> dict:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Erreur récupération utilisateur: {e}")
            return None

    def get_user_by_discord_id(self, discord_id: int) -> dict:
        return self.get_user(discord_id)

import sqlite3
import os
from config import settings
from models.user import User
from utils.logger import logger

class UserRepository:
    def __init__(self):
        # Crée le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(settings.local_db_path), exist_ok=True)
        self.conn = sqlite3.connect(settings.local_db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                discord_id INTEGER PRIMARY KEY,
                steam_id TEXT UNIQUE,
                name TEXT,
                age TEXT,
                crime TEXT,
                sentence TEXT
            )
        """)
        self.conn.commit()

    def link_steam_id(self, discord_id: int, steam_id: str, name: str, age: str, crime: str, sentence: str) -> bool:
        try:
            self.conn.execute(
                "INSERT INTO users (discord_id, steam_id, name, age, crime, sentence) VALUES (?, ?, ?, ?, ?, ?)",
                (discord_id, steam_id, name, age, crime, sentence)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def is_user_registered(self, discord_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE discord_id = ?", (discord_id,))
        return cursor.fetchone() is not None

    def get_user(self, discord_id: int) -> User:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        if row:
            return User(discord_id=row[0], steam_id=row[1], name=row[2], age=row[3], crime=row[4], sentence=row[5])
        return None

# utils/action_logger.py
import sqlite3
from datetime import datetime
from config.settings import settings

class ActionLogger:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        """Initialise la table des logs si elle n'existe pas"""
        with sqlite3.connect(settings.local_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS action_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    target TEXT,
                    status TEXT,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def log_action(self, user_id: int, action_type: str, target: str, status: str, message: str):
        """Enregistre une action dans les logs"""
        try:
            with sqlite3.connect(settings.local_db_path) as conn:
                conn.execute('''
                    INSERT INTO action_logs
                    (user_id, action_type, target, status, message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, action_type, target, status, message))
                conn.commit()
        except Exception as e:
            print(f"Erreur enregistrement log: {e}")

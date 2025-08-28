import sqlite3
from config.settings import settings
from utils.logger import logger
from datetime import datetime, timedelta
import os

class ScumRepository:
    def __init__(self):
        self.db_path = settings.scum_bot_db_path
        self.last_sync = None
        self.sync_interval = timedelta(minutes=5)

    def _ensure_db_exists(self, ftp_service):
        """Vérifie et télécharge la base SCUM si nécessaire"""
        if not os.path.exists(self.db_path) or not self.last_sync or \
           (datetime.now() - self.last_sync) > self.sync_interval:
            logger.info("Synchronisation de SCUM.db nécessaire...")
            if not ftp_service.download_scum_db():
                return False
            self.last_sync = datetime.now()
        return True

    def get_user_scum_id(self, steam_id: str) -> int:
        """Récupère l'ID SCUM d'un utilisateur depuis son SteamID"""
        try:
            if not os.path.exists(self.db_path):
                return None
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM user_profile WHERE user_id = ?', (steam_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Erreur SQL (user_profile): {e}")
            return None

    def get_bank_balance(self, scum_id: int) -> int:
        """Récupère le solde bancaire d'un utilisateur"""
        try:
            if not os.path.exists(self.db_path):
                return None
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT account_balance FROM bank_account_registry_currencies
                WHERE bank_account_id = ? AND currency_type = 1
            ''', (scum_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Erreur SQL (bank_account): {e}")
            return None

    def get_top_balances(self, limit: int = 5) -> list[tuple]:
        """Retourne une liste de tuples (name, account_balance)"""
        try:
            if not os.path.exists(self.db_path):
                return []

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT up.name, bar.account_balance
                FROM bank_account_registry_currencies bar
                JOIN user_profile up ON bar.bank_account_id = up.id
                WHERE bar.currency_type = 1
                ORDER BY bar.account_balance DESC
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Erreur SQL (top balances): {e}")
            return []

    def update_bank_balance(self, scum_id: int, new_balance: int) -> bool:
        """Met à jour le solde bancaire d'un utilisateur"""
        try:
            if not os.path.exists(self.db_path):
                return False
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE bank_account_registry_currencies
                SET account_balance = ?
                WHERE bank_account_id = ? AND currency_type = 1
            ''', (new_balance, scum_id))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Erreur mise à jour solde: {e}")
            return False

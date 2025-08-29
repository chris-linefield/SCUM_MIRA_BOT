import ftplib
import os
import sqlite3
from config import settings
from utils.logger import logger

class FTPRepository:
    def __init__(self):
        self.ftp = ftplib.FTP()
        self.ftp.connect(settings.ftp_host, settings.ftp_port)
        self.ftp.login(settings.ftp_user, settings.ftp_pass)

    def download_scum_db(self, local_path: str) -> bool:
        try:
            with open(local_path, "wb") as f:
                self.ftp.retrbinary(f"RETR {settings.ftp_db_path}", f.write)
            logger.info("SCUM.db téléchargé avec succès.")
            return True
        except Exception as e:
            logger.error(f"Erreur FTP: {e}")
            return False

    def close(self):
        self.ftp.quit()

def get_scum_db_connection():
    if not os.path.exists(settings.scum_db_path):
        ftp = FTPRepository()
        if not ftp.download_scum_db(settings.scum_db_path):
            return None
        ftp.close()
    return sqlite3.connect(settings.scum_db_path)

def copy_bank_accounts_to_local_db():
    scum_conn = get_scum_db_connection()
    if not scum_conn:
        logger.error("Impossible de se connecter à la base de données SCUM.db.")
        return False

    local_conn = sqlite3.connect(settings.local_db_path)

    try:
        # Créer la table bank_account_registry_currencies dans la base locale si elle n'existe pas
        local_conn.execute("""
            CREATE TABLE IF NOT EXISTS bank_account_registry_currencies (
                id INTEGER PRIMARY KEY,
                map_id INTEGER,
                user_profile_id INTEGER,
                bank_account_id INTEGER NOT NULL,
                currency_type INTEGER NOT NULL,
                account_balance INTEGER,
                FOREIGN KEY(bank_account_id) REFERENCES bank_account_registry(id) ON DELETE CASCADE,
                FOREIGN KEY(map_id) REFERENCES map(id) ON DELETE CASCADE,
                FOREIGN KEY(user_profile_id) REFERENCES user_profile(id) ON DELETE CASCADE
            )
        """)

        # Copier les données de la table bank_account_registry_currencies
        scum_cursor = scum_conn.cursor()
        scum_cursor.execute("SELECT * FROM bank_account_registry_currencies")
        rows = scum_cursor.fetchall()

        if rows:
            local_conn.executemany(
                "INSERT OR REPLACE INTO bank_account_registry_currencies VALUES (?, ?, ?, ?, ?, ?)",
                rows
            )

        local_conn.commit()
        logger.info("Table bank_account_registry_currencies copiée avec succès dans scum_bot.db.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la copie de la table bank_account_registry_currencies: {e}")
        return False
    finally:
        scum_conn.close()
        local_conn.close()
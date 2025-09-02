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

def copy_tables_to_local_db():
    scum_conn = get_scum_db_connection()
    if not scum_conn:
        logger.error("Impossible de se connecter à la base de données SCUM.db.")
        return False

    local_conn = sqlite3.connect(settings.local_db_path)

    try:
        # Liste des tables à copier
        tables_to_copy = [
            "user_profile",
            "bank_account_registry",
            "bank_account_registry_currencies"
        ]

        for table in tables_to_copy:
            # Supprimer l'ancienne table si elle existe
            local_conn.execute(f"DROP TABLE IF EXISTS {table}")

            # Créer la table dans la base locale
            scum_cursor = scum_conn.cursor()
            scum_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
            create_table_sql = scum_cursor.fetchone()
            if create_table_sql:
                local_conn.execute(create_table_sql[0])

                # Copier les données
                scum_cursor.execute(f"SELECT * FROM {table}")
                rows = scum_cursor.fetchall()
                if rows:
                    placeholders = ', '.join(['?'] * len(rows[0]))
                    local_conn.executemany(
                        f"INSERT INTO {table} VALUES ({placeholders})",
                        rows
                    )

        local_conn.commit()
        logger.info("Tables écrasées et recopiées avec succès dans scum_bot.db.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la copie des tables: {e}")
        return False
    finally:
        scum_conn.close()
        local_conn.close()
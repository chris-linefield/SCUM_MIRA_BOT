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
    # Crée le dossier data s'il n'existe pas
    os.makedirs(os.path.dirname(settings.scum_db_path), exist_ok=True)

    if not os.path.exists(settings.scum_db_path):
        ftp = FTPRepository()
        if not ftp.download_scum_db(settings.scum_db_path):
            return None
        ftp.close()
    return sqlite3.connect(settings.scum_db_path)

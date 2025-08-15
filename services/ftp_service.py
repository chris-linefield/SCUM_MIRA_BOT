from ftplib import FTP
import os
from config.settings import settings
from utils.logger import logger

class FTPService:
    def download_scum_db(self) -> bool:
        """Télécharge la base de données SCUM depuis le serveur FTP"""
        try:
            os.makedirs(os.path.dirname(settings.scum_bot_db_path), exist_ok=True)

            with FTP() as ftp:
                ftp.connect(settings.ftp_host, settings.ftp_port)
                ftp.login(settings.ftp_user, settings.ftp_pass)

                with open(settings.scum_bot_db_path, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {settings.ftp_db_path}', local_file.write)

            logger.info(f"Base SCUM téléchargée vers {settings.scum_bot_db_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur FTP: {e}")
            return False

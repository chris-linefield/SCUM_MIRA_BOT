# services/bank_service.py
from repositories.user_repository import UserRepository
from repositories.scum_repository import ScumRepository
from services.ftp_service import FTPService
from config.settings import settings
from utils.action_logger import ActionLogger

class BankService:
    def __init__(self):
        self.scum_repo = ScumRepository()
        self.user_repo = UserRepository()
        self.ftp_service = FTPService()
        self.logger = ActionLogger()

    async def get_user_balance(self, discord_id: int) -> int:
        """Récupère le solde bancaire d'un utilisateur"""
        try:
            # Récupère l'utilisateur
            user = self.user_repo.get_user(discord_id)
            if not user or 'steam_id' not in user or not user['steam_id']:
                return -2  # SteamID non lié

            # Télécharge la base SCUM
            if not self.ftp_service.download_scum_db():
                return -1  # Erreur FTP

            # Récupère le solde
            scum_id = self.scum_repo.get_user_scum_id(user['steam_id'])
            if not scum_id:
                return -3  # ID SCUM introuvable

            balance = self.scum_repo.get_bank_balance(scum_id)
            return balance
        except Exception as e:
            self.logger.log_action(discord_id, "balance_check", "error", "failed", str(e))
            return -4  # Erreur inattendue

    async def withdraw(self, discord_id: int, amount: int) -> tuple[bool, str]:
        """Retire un montant du solde bancaire"""
        try:
            # Récupère l'utilisateur
            user = self.user_repo.get_user(discord_id)
            if not user or 'steam_id' not in user or not user['steam_id']:
                return False, "SteamID non lié."

            # Vérifie le solde
            balance = await self.get_user_balance(discord_id)
            if balance < 0:
                return False, "Erreur de connexion à la base SCUM."
            if balance < amount:
                return False, f"Solde insuffisant (actuel: {balance})."

            # Met à jour le solde
            scum_id = self.scum_repo.get_user_scum_id(user['steam_id'])
            if not scum_id:
                return False, "ID SCUM introuvable."

            new_balance = balance - amount
            if not self.scum_repo.update_bank_balance(scum_id, new_balance):
                return False, "Échec de la mise à jour du solde."

            self.logger.log_action(discord_id, "withdraw", f"Montant: {amount}", "success", f"Nouveau solde: {new_balance}")
            return True, f"Retrait de {amount}. Nouveau solde: {new_balance}."
        except Exception as e:
            self.logger.log_action(discord_id, "withdraw", "error", "failed", str(e))
            return False, f"Erreur inattendue: {str(e)}"

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

    async def get_user_balance(self, discord_id: int) -> tuple[int, str]:
        """Retourne (solde, message) ou (-1, message_erreur)"""
        try:
            user = self.user_repo.get_user(discord_id)
            if not user or 'steam_id' not in user or not user['steam_id']:
                return -2, "SteamID non lié à votre compte Discord."

            if not self.ftp_service.download_scum_db():
                return -1, "Échec de la synchronisation avec la base SCUM (FTP)."

            scum_id = self.scum_repo.get_user_scum_id(user['steam_id'])
            if not scum_id:
                return -3, f"ID SCUM introuvable pour le SteamID : {user['steam_id']}"

            balance = self.scum_repo.get_bank_balance(scum_id)
            if balance is None:
                return -4, "Aucun solde trouvé pour ce compte."

            return balance, "Succès"
        except Exception as e:
            self.logger.log_action(discord_id, "balance_check", "error", "failed", str(e))
            return -4, f"Erreur inattendue : {str(e)}"

    async def get_top_balances(self, limit: int = 5) -> tuple[list[tuple], str]:
        """Retourne (liste des soldes, message) ou ([], message_erreur)"""
        try:
            if not self.ftp_service.download_scum_db():
                return [], "Échec de la synchronisation avec la base SCUM (FTP)."

            top_balances = self.scum_repo.get_top_balances(limit)
            if not top_balances:
                return [], "Aucun solde trouvé."

            return top_balances, "Succès"
        except Exception as e:
            self.logger.log_action(0, "top_balance_check", "error", "failed", str(e))
            return [], f"Erreur inattendue : {str(e)}"

    async def withdraw(self, discord_id: int, amount: int) -> tuple[bool, str]:
        """Retire un montant du solde bancaire"""
        try:
            user = self.user_repo.get_user(discord_id)
            if not user or 'steam_id' not in user or not user['steam_id']:
                return False, "SteamID non lié."

            balance, message = await self.get_user_balance(discord_id)
            if balance < 0:
                return False, message

            if balance < amount:
                return False, f"Solde insuffisant (actuel: {balance})."

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

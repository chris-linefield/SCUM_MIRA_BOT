import sqlite3
from config import settings
from utils.logger import logger

def get_bank_balance(steam_id: str) -> int:
    """Récupère le solde bancaire d'un joueur depuis scum_bot.db."""
    conn = sqlite3.connect(settings.local_db_path)
    try:
        cursor = conn.cursor()

        # 1. Trouver l'id du joueur
        cursor.execute("SELECT id FROM user_profile WHERE user_id = ?", (steam_id,))
        user_profile_result = cursor.fetchone()
        if not user_profile_result:
            logger.error(f"Aucun utilisateur trouvé avec le steam_id: {steam_id}")
            return 0
        user_profile_id = user_profile_result[0]

        # 2. Trouver l'id du compte bancaire
        cursor.execute(
            "SELECT id FROM bank_account_registry WHERE account_owner_user_profile_id = ?",
            (user_profile_id,)
        )
        bank_account_result = cursor.fetchone()
        if not bank_account_result:
            logger.error(f"Aucun compte bancaire trouvé pour l'utilisateur avec l'id: {user_profile_id}")
            return 0
        bank_account_id = bank_account_result[0]

        # 3. Trouver le solde (currency_type = 1 pour la monnaie principale)
        cursor.execute(
            """
            SELECT account_balance
            FROM bank_account_registry_currencies
            WHERE bank_account_id = ? AND currency_type = 1
            """,
            (bank_account_id,)
        )
        balance_result = cursor.fetchone()
        if not balance_result:
            logger.error(f"Aucun solde trouvé pour le compte bancaire avec l'id: {bank_account_id}")
            return 0

        return balance_result[0]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du solde bancaire: {e}")
        return 0
    finally:
        conn.close()

def update_bank_balance(steam_id: str, new_balance: int) -> bool:
    """Met à jour le solde bancaire d'un joueur dans scum_bot.db."""
    conn = sqlite3.connect(settings.local_db_path)
    try:
        cursor = conn.cursor()

        # 1. Trouver l'id du joueur
        cursor.execute("SELECT id FROM user_profile WHERE user_id = ?", (steam_id,))
        user_profile_result = cursor.fetchone()
        if not user_profile_result:
            logger.error(f"Aucun utilisateur trouvé avec le steam_id: {steam_id}")
            return False
        user_profile_id = user_profile_result[0]

        # 2. Trouver l'id du compte bancaire
        cursor.execute(
            "SELECT id FROM bank_account_registry WHERE account_owner_user_profile_id = ?",
            (user_profile_id,)
        )
        bank_account_result = cursor.fetchone()
        if not bank_account_result:
            logger.error(f"Aucun compte bancaire trouvé pour l'utilisateur avec l'id: {user_profile_id}")
            return False
        bank_account_id = bank_account_result[0]

        # 3. Mettre à jour le solde (currency_type = 1 pour la monnaie principale)
        cursor.execute(
            """
            UPDATE bank_account_registry_currencies
            SET account_balance = ?
            WHERE bank_account_id = ? AND currency_type = 1
            """,
            (new_balance, bank_account_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du solde bancaire: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

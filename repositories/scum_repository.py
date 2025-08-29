import sqlite3
from repositories.ftp_repository import get_scum_db_connection
from utils.logger import logger

def get_user_balance(steam_id: str) -> int:
    # Étape 1: Récupérer l'ID SCUM de l'utilisateur depuis la table user
    conn = get_scum_db_connection()
    if not conn:
        logger.error("Impossible de se connecter à la base de données SCUM.")
        return 0

    try:
        cursor = conn.cursor()

        # Étape 2: Trouver l'ID de l'utilisateur dans user_profile
        cursor.execute("""
            SELECT id FROM user_profile
            WHERE user_id = ?
        """, (steam_id,))
        user_profile_result = cursor.fetchone()
        if not user_profile_result:
            logger.error(f"Aucun utilisateur trouvé avec le SteamID: {steam_id}")
            return 0
        user_profile_id = user_profile_result[0]

        # Étape 3: Trouver l'ID du compte bancaire dans bank_account_registry
        cursor.execute("""
            SELECT id FROM bank_account_registry
            WHERE account_owner_user_profile_id = ?
        """, (user_profile_id,))
        bank_account_result = cursor.fetchone()
        if not bank_account_result:
            logger.error(f"Aucun compte bancaire trouvé pour l'utilisateur avec l'ID: {user_profile_id}")
            return 0
        bank_account_id = bank_account_result[0]

        # Étape 4: Récupérer le solde où currency_type = 1
        cursor.execute("""
            SELECT account_balance FROM bank_account_registry_currencies
            WHERE bank_account_id = ? AND currency_type = 1
        """, (bank_account_id,))
        balance_result = cursor.fetchone()
        if not balance_result:
            logger.error(f"Aucun solde trouvé pour le compte bancaire avec l'ID: {bank_account_id}")
            return 0

        return balance_result[0]
    except sqlite3.Error as e:
        logger.error(f"Erreur SQL lors de la récupération du solde: {e}")
        return 0
    finally:
        conn.close()
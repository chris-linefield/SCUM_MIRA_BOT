from repositories.ftp_repository import get_scum_db_connection
from utils.logger import logger

def get_user_balance(steam_id: str) -> int:
    """
    Récupère le solde bancaire d'un joueur à partir de son Steam ID.
    Étapes :
    1. Trouver l'ID du profil utilisateur dans la table `user` avec le Steam ID.
    2. Trouver l'ID du compte bancaire dans la table `bank_account_registry` avec l'user_profile_id.
    3. Récupérer le solde bancaire dans la table `bank_account_registry_currencies` avec le bank_account_id et currency_type = 1.
    """
    conn = get_scum_db_connection()
    if not conn:
        logger.error("Impossible de se connecter à la base de données SCUM.")
        return 0

    try:
        cursor = conn.cursor()

        # Étape 1 : Trouver l'ID du profil utilisateur dans la table `user`
        cursor.execute("SELECT id FROM user WHERE id = ?", (steam_id,))
        user_row = cursor.fetchone()
        if not user_row:
            logger.error(f"Aucun utilisateur trouvé avec le Steam ID : {steam_id}")
            return 0

        user_id = user_row[0]

        # Étape 2 : Trouver l'user_profile_id dans la table `user_profile`
        cursor.execute("SELECT id FROM user_profile WHERE user_id = ?", (user_id,))
        user_profile_row = cursor.fetchone()
        if not user_profile_row:
            logger.error(f"Aucun profil utilisateur trouvé pour l'ID utilisateur : {user_id}")
            return 0

        user_profile_id = user_profile_row[0]

        # Étape 3 : Trouver l'ID du compte bancaire dans la table `bank_account_registry`
        cursor.execute("SELECT id FROM bank_account_registry WHERE account_owner_user_profile_id = ?", (user_profile_id,))
        bank_account_row = cursor.fetchone()
        if not bank_account_row:
            logger.error(f"Aucun compte bancaire trouvé pour l'user_profile_id : {user_profile_id}")
            return 0

        bank_account_id = bank_account_row[0]

        # Étape 4 : Récupérer le solde bancaire dans la table `bank_account_registry_currencies`
        cursor.execute("""
            SELECT account_balance
            FROM bank_account_registry_currencies
            WHERE bank_account_id = ? AND currency_type = 1
        """, (bank_account_id,))
        balance_row = cursor.fetchone()
        if not balance_row:
            logger.error(f"Aucun solde trouvé pour le bank_account_id : {bank_account_id}")
            return 0

        balance = balance_row[0]
        return balance

    except Exception as e:
        logger.error(f"Erreur lors de la récupération du solde : {e}")
        return 0

    finally:
        conn.close()

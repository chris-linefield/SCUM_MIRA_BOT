from repositories.ftp_repository import get_scum_db_connection

def get_user_balance(steam_id: str) -> int:
    conn = get_scum_db_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM user_profile
            WHERE user_id = ?
        """, (steam_id,))
        user_profile_result = cursor.fetchone()
        if not user_profile_result:
            return 0
        user_profile_id = user_profile_result[0]

        cursor.execute("""
            SELECT id FROM bank_account_registry
            WHERE account_owner_user_profile_id = ?
        """, (user_profile_id,))
        bank_account_result = cursor.fetchone()
        if not bank_account_result:
            return 0
        bank_account_id = bank_account_result[0]

        cursor.execute("""
            SELECT account_balance FROM bank_account_registry_currencies
            WHERE bank_account_id = ? AND currency_type = 1
        """, (bank_account_id,))
        balance_result = cursor.fetchone()
        if not balance_result:
            return 0
        balance = balance_result[0]

        return balance
    finally:
        conn.close()
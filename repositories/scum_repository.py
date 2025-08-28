from repositories.ftp_repository import get_scum_db_connection

def get_user_balance(steam_id: str) -> int:
    conn = get_scum_db_connection()
    if not conn:
        return 0
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT account_balance
            FROM bank_account_registry_currencies
            JOIN user_profile ON user_profile_id = user_profile.id
            JOIN user ON user_id = user.id
            WHERE user.id = ?
        """, (steam_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        conn.close()

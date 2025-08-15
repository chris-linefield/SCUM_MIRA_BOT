from pydantic_settings import BaseSettings
from config.constants import AUTHORIZED_ROLE_ID

class Settings(BaseSettings):
    # Discord
    discord_token: str
    discord_guild_id: int
    discord_channel_id: int
    discord_role_garagiste: int = AUTHORIZED_ROLE_ID

    # Base de données
    local_db_path: str = "./data/bot.db"
    scum_bot_db_path: str = "./data/scum_bot.db"

    # FTP SCUM
    ftp_host: str
    ftp_port: int
    ftp_user: str
    ftp_pass: str
    ftp_db_path: str

    class Config:
        env_file = ".env"

settings = Settings()

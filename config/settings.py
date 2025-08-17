from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Discord
    discord_token: str
    discord_guild_id: int
    discord_channel_id: int

    # Rôles (définis dans constants.py)
    discord_role_garagiste: int = 1405192378066796606
    discord_role_armurier: int = 1405501043684545556
    discord_role_moto: int = 1406507024082276435
    discord_role_quincaillerie: int = 1405501176786583593
    discord_role_restaurateur: int = 1405501264187625533
    discord_role_superette: int = 1405501210110332988

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

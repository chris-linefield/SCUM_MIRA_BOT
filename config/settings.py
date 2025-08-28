from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Discord
    discord_token: str
    discord_guild_id: int

    # Local DB
    local_db_path: str = "./data/scum_bot.db"
    scum_db_path: str = "./data/SCUM.db"

    # FTP
    ftp_host: str
    ftp_port: int
    ftp_user: str
    ftp_pass: str
    ftp_db_path: str

    class Config:
        env_file = ".env"

settings = Settings()

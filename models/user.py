from pydantic import BaseModel

class User(BaseModel):
    discord_id: int
    steam_id: str
    name: str
    age: str
    crime: str
    sentence: str

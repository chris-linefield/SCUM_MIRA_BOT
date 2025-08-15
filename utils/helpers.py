import re

def is_valid_steam_id(steam_id: str) -> bool:
    return bool(re.match(r"^\d{17}$", steam_id))

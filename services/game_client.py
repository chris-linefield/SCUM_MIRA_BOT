import pyautogui
import time
import psutil
from utils.logger import logger
from config.constants import DELAY_BETWEEN_ACTIONS

class GameClient:
    @staticmethod
    def is_scum_running() -> bool:
        return "scum.exe" in (p.name().lower() for p in psutil.process_iter())

    @staticmethod
    def spawn_item(item_id: str, count: int = 1):
        if not GameClient.is_scum_running():
            logger.error("scum.exe n'est pas en cours d'exécution.")
            return False
        try:
            pyautogui.press("t")
            time.sleep(DELAY_BETWEEN_ACTIONS)
            pyautogui.write(f"#SpawnItem {item_id} {count}")
            time.sleep(DELAY_BETWEEN_ACTIONS)
            pyautogui.press("enter")
            logger.info(f"Item {item_id} x{count} spawné.")
            return True
        except Exception as e:
            logger.error(f"Erreur pyautogui: {e}")
            return False

    @staticmethod
    def spawn_vehicle(vehicle_id: str):
        if not GameClient.is_scum_running():
            logger.error("scum.exe n'est pas en cours d'exécution.")
            return False
        try:
            pyautogui.press("t")
            time.sleep(DELAY_BETWEEN_ACTIONS)
            pyautogui.write(f"#SpawnVehicle {vehicle_id}")
            time.sleep(DELAY_BETWEEN_ACTIONS)
            pyautogui.press("enter")
            logger.info(f"Véhicule {vehicle_id} spawné.")
            return True
        except Exception as e:
            logger.error(f"Erreur pyautogui: {e}")
            return False

    @staticmethod
    def announce(message: str):
        if not GameClient.is_scum_running():
            logger.error("scum.exe n'est pas en cours d'exécution.")
            return False
        try:
            pyautogui.press("t")
            time.sleep(DELAY_BETWEEN_ACTIONS)
            pyautogui.write(f"#Announce {message}")
            time.sleep(DELAY_BETWEEN_ACTIONS)
            pyautogui.press("enter")
            logger.info(f"Annonce envoyée: {message}")
            return True
        except Exception as e:
            logger.error(f"Erreur pyautogui: {e}")
            return False

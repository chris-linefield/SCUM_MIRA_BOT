import pyautogui
import time
import pygetwindow as gw
import pyperclip
from utils.logger import logger
from typing import Tuple
import asyncio

class ScumManager:
    @staticmethod
    def is_scum_running() -> bool:
        try:
            return any("SCUM" in title for title in gw.getAllTitles())
        except Exception as e:
            logger.error(f"Erreur vérification SCUM: {e}")
            return False

    @staticmethod
    def focus_scum_window() -> bool:
        try:
            scum_window = next(w for w in gw.getWindowsWithTitle("SCUM") if w.isActive)
            scum_window.activate()
            return True
        except Exception as e:
            logger.error(f"Erreur focus fenêtre SCUM: {e}")
            return False

    @staticmethod
    def send_command(command: str) -> Tuple[bool, str]:
        if not ScumManager.is_scum_running():
            return False, "SCUM n'est pas ouvert"

        if not ScumManager.focus_scum_window():
            return False, "Impossible de focuser SCUM"

        try:
            pyautogui.press('t')
            time.sleep(2.0)

            pyperclip.copy(command)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2.0)

            pyautogui.press('enter')
            time.sleep(2.0)

            pyautogui.press('enter')
            time.sleep(2.0)

            return True, "Commande envoyée"
        except Exception as e:
            logger.error(f"Erreur envoi commande: {str(e)}")
            return False, f"Erreur: {str(e)}"

async def send_scum_command(command: str, user_id: int, max_retries: int = 3) -> Tuple[bool, str]:
    from utils.action_logger import ActionLogger
    logger = ActionLogger()

    for attempt in range(max_retries):
        if not ScumManager.is_scum_running():
            logger.log_action(user_id, "scum_command", command, "failed", "SCUM non ouvert")
            if attempt == max_retries - 1:
                return False, "SCUM n'est pas ouvert. Veuillez lancer le jeu."
            await asyncio.sleep(5)
            continue

        success, message = ScumManager.send_command(command)
        if success:
            logger.log_action(user_id, "scum_command", command, "success", "Commande envoyée")
            return True, "Commande envoyée avec succès"
        else:
            logger.log_action(user_id, "scum_command", command, "failed", message)
            if attempt == max_retries - 1:
                return False, f"Échec après {max_retries} tentatives: {message}"
            await asyncio.sleep(3)

    return False, f"Échec après {max_retries} tentatives"
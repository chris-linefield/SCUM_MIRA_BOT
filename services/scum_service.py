# services/scum_service.py
import pyautogui
import time
import pygetwindow as gw
import pyperclip
from utils.logger import logger
from typing import Tuple

class ScumManager:
    @staticmethod
    def is_scum_running() -> bool:
        """Vérifie si SCUM est en cours d'exécution"""
        try:
            return any("SCUM" in title for title in gw.getAllTitles())
        except Exception as e:
            logger.error(f"Erreur vérification SCUM: {e}")
            return False

    @staticmethod
    def focus_scum_window() -> bool:
        """Focus la fenêtre SCUM"""
        try:
            scum_window = next(w for w in gw.getWindowsWithTitle("SCUM") if w.isActive)
            scum_window.activate()
            return True
        except Exception as e:
            logger.error(f"Erreur focus fenêtre SCUM: {e}")
            return False

    @staticmethod
    def send_command(command: str) -> Tuple[bool, str]:
        """
        Envoie une commande complète à SCUM avec la séquence:
        1. Appuie sur T pour ouvrir le chat
        2. Colle la commande (Ctrl+V)
        3. Valide avec Entrée
        """
        if not ScumManager.is_scum_running():
            return False, "SCUM n'est pas ouvert"

        if not ScumManager.focus_scum_window():
            return False, "Impossible de focuser SCUM"

        try:
            # 1. Ouvre le chat
            pyautogui.press('t')
            time.sleep(0.8)  # Attend l'ouverture du chat

            # 2. Colle la commande
            pyperclip.copy(command)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)  # Attend le collage

            # 3. Valide avec Entrée
            pyautogui.press('enter')
            time.sleep(0.5)  # Attend l'envoi

            return True, "Commande envoyée"
        except Exception as e:
            logger.error(f"Erreur envoi commande: {str(e)}")
            return False, f"Erreur: {str(e)}"

async def send_scum_command(command: str, user_id: int) -> Tuple[bool, str]:
    """Envoie une commande à SCUM avec gestion des erreurs et logging"""
    from utils.action_logger import ActionLogger
    logger = ActionLogger()

    if not ScumManager.is_scum_running():
        logger.log_action(user_id, "scum_command", command, "failed", "SCUM non ouvert")
        return False, "SCUM n'est pas ouvert. Veuillez lancer le jeu."

    success, message = ScumManager.send_command(command)
    if not success:
        logger.log_action(user_id, "scum_command", command, "failed", message)
        return False, f"Échec envoi commande: {message}"

    logger.log_action(user_id, "scum_command", command, "success", "Commande envoyée")
    return True, "Commande envoyée avec succès"

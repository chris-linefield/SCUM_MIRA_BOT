import os
import subprocess
import psutil
import pyautogui
import asyncio
import pydirectinput
import pyperclip
import pygetwindow as gw
from datetime import datetime, time as datetime_time, timedelta
from typing import Tuple
from utils.logger import logger

pydirectinput.FAILSAFE = False

class ScumManager:
    def __init__(self):
        self.steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
        self.scum_app_id = "513710"
        self.button_continue_pos = (186, 675)
        self.reboot_times = [
            datetime_time(1, 0),   # 01H
            datetime_time(7, 0),   # 07H
            datetime_time(13, 0),  # 13H
            datetime_time(19, 0)   # 19H
        ]
        self.log_file = "logs/scum_reboot.log"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def is_scum_running(self):
        """Vérifie si SCUM est en cours d'exécution."""
        try:
            return "SCUM.exe" in [p.name() for p in psutil.process_iter()]
        except Exception as e:
            logger.error(f"Erreur vérification SCUM: {e}")
            return False

    async def _kill_scum(self):
        """Ferme SCUM de manière asynchrone."""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == "SCUM.exe":
                    proc.kill()
            logger.info("SCUM fermé avec succès.")
            await asyncio.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture: {e}")
            return False

    async def launch_scum(self):
        """Lance SCUM et clique sur CONTINUER."""
        try:
            subprocess.Popen([self.steam_path, "-applaunch", self.scum_app_id])
            logger.info("SCUM lancé. Attente de 45 secondes...")
            await asyncio.sleep(45)
            # Trouve la fenêtre SCUM
            scum_window = None
            for window in gw.getWindowsWithTitle("SCUM"):
                scum_window = window
                break
            if scum_window:
                scum_window.activate()
                await asyncio.sleep(2)
                # Envoie Ctrl+D
                pydirectinput.keyDown('ctrl')
                pydirectinput.press('d')
                pydirectinput.keyUp('ctrl')
                logger.info("Combinaison Ctrl+D envoyée.")
                await asyncio.sleep(2)
                # Clique sur le bouton Continuer
                pydirectinput.moveTo(*self.button_continue_pos)
                pydirectinput.click()
                logger.info(f"Cliqué sur CONTINUER à {self.button_continue_pos}")
                return True
            else:
                logger.error("Fenêtre SCUM introuvable.")
                return False
        except Exception as e:
            logger.error(f"Erreur dans launch_scum: {e}")
            return False

    async def reboot_scum(self):
        """Redémarre SCUM complètement."""
        try:
            logger.info("🔄 Redémarrage de SCUM...")
            if self.is_scum_running():
                if not await self._kill_scum():
                    return False
                await asyncio.sleep(3)
            if not await self.launch_scum():
                return False
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== Reboot SCUM - {datetime.now()} ===\n")
                f.write(f"Bouton CONTINUER cliqué à {self.button_continue_pos}\n")
                f.write("========================================\n")
            logger.info("SCUM relancé avec succès!")
            return True
        except Exception as e:
            logger.error(f"Erreur dans reboot_scum: {e}")
            return False

    def get_next_reboot_time(self):
        """Calcule le prochain horaire de reboot."""
        now = datetime.now()
        today = now.date()
        for reboot_time in self.reboot_times:
            next_reboot = datetime.combine(today, reboot_time)
            if next_reboot > now:
                return next_reboot
        tomorrow = today + timedelta(days=1)
        return datetime.combine(tomorrow, self.reboot_times[0])

    async def send_reboot_warning(self):
        """Envoie une annonce 5 minutes avant le redémarrage."""
        message = "#Announce Réinitialisation des puces BCU dans 5 minutes, allongez-vous !"
        success, result_message = await self.send_scum_command(message)
        if success:
            logger.info(f"Annonce de redémarrage envoyée: {message}")
        else:
            logger.error(f"Erreur lors de l'envoi de l'annonce de redémarrage: {result_message}")

    async def start_periodic_reboot(self):
        """Boucle infinie pour les reboots périodiques et les annonces."""
        while True:
            try:
                now = datetime.now()
                next_reboot = self.get_next_reboot_time()
                time_until_reboot = (next_reboot - now).total_seconds()
                # Si le redémarrage est dans 5 minutes, envoyer l'annonce
                if 0 < time_until_reboot <= 300:  # 300 secondes = 5 minutes
                    await self.send_reboot_warning()
                    await asyncio.sleep(300)  # Attendre 5 minutes avant le redémarrage
                    continue
                if time_until_reboot <= 0:
                    await self.reboot_scum()
                    await asyncio.sleep(60)  # Attendre 1 minute avant de vérifier à nouveau
                else:
                    logger.info(f"Prochain reboot prévu à {next_reboot.strftime('%H:%M')}")
                    await asyncio.sleep(60)  # Vérifier toutes les minutes
            except asyncio.CancelledError:
                logger.info("Tâche de reboot annulée")
                break
            except Exception as e:
                logger.error(f"Erreur dans start_periodic_reboot: {e}")
                await asyncio.sleep(60)

    def focus_scum_window(self) -> bool:
        """Active la fenêtre SCUM."""
        try:
            scum_window = next(w for w in gw.getWindowsWithTitle("SCUM") if w)
            scum_window.activate()
            return True
        except Exception as e:
            logger.error(f"Erreur focus fenêtre SCUM: {e}")
            return False

    def send_command(self, command: str) -> Tuple[bool, str]:
        """Envoie une commande à SCUM."""
        if not self.is_scum_running():
            return False, "SCUM n'est pas ouvert"
        if not self.focus_scum_window():
            return False, "Impossible de focuser SCUM"
        try:
            pyautogui.press('t')
            pyautogui.sleep(2.0)
            pyperclip.copy(command)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.sleep(2.0)
            pyautogui.press('enter')
            pyautogui.sleep(2.0)
            pyautogui.press('enter')
            pyautogui.sleep(2.0)
            return True, "Commande envoyée"
        except Exception as e:
            logger.error(f"Erreur envoi commande: {str(e)}")
            return False, f"Erreur: {str(e)}"

async def send_scum_command(command: str, max_retries: int = 3) -> Tuple[bool, str]:
    """Envoie une commande à SCUM avec gestion des erreurs et des réessais."""
    scum_manager = ScumManager()  # Instancie ScumManager
    for attempt in range(max_retries):
        if not scum_manager.is_scum_running():
            if attempt == max_retries - 1:
                return False, "SCUM n'est pas ouvert. Veuillez lancer le jeu."
            await asyncio.sleep(5)
            continue
        success, message = scum_manager.send_command(command)
        if success:
            return True, "Commande envoyée avec succès"
        else:
            if attempt == max_retries - 1:
                return False, f"Échec après {max_retries} tentatives: {message}"
            await asyncio.sleep(3)
    return False, f"Échec après {max_retries} tentatives"

import subprocess
import asyncio
import psutil
import pydirectinput
from datetime import datetime, time as datetime_time, timedelta
from repositories.scum_repository import logger

pydirectinput.FAILSAFE = False  # Désactive le fail-safe pour les tests

class SCUMManager:
    def __init__(self):
        self.steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
        self.scum_app_id = "513710"
        self.button_continue_pos = (186, 675)  # Coordonnées pour ton écran secondaire
        self.reboot_times = [
            datetime_time(1, 0),   # 01H
            datetime_time(7, 0),   # 07H
            datetime_time(13, 0),  # 13H
            datetime_time(19, 0)   # 19H
        ]
        self.log_file = "logs/scum_reboot.log"

    def is_scum_running(self):
        """Vérifie si SCUM est en cours d'exécution (synchrone)."""
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
            await asyncio.sleep(2)  # Temps pour la fermeture
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

            pydirectinput.keyDown('ctrl')
            pydirectinput.press('d')
            pydirectinput.keyUp('ctrl')
            logger.info("Combinaison Ctrl+D envoyée.")
            await asyncio.sleep(2)
            pydirectinput.moveTo(*self.button_continue_pos)
            pydirectinput.click()
            logger.info(f"Cliqué sur CONTINUER à {self.button_continue_pos}")
            return True
        except Exception as e:
            logger.error(f"Erreur dans launch_scum: {e}", exc_info=True)
            return False

    async def reboot_scum(self):
        """Redémarre SCUM complètement."""
        try:
            logger.info("🔄 Redémarrage de SCUM...")
            if self.is_scum_running():
                if not await self._kill_scum():
                    return False
                await asyncio.sleep(3)  # Attend après la fermeture

            if not await self.launch_scum():
                return False

            # Log
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== Reboot SCUM - {datetime.now()} ===\n")
                f.write(f"Bouton CONTINUER cliqué à {self.button_continue_pos}\n")
                f.write("========================================\n")

            logger.info("SCUM relancé avec succès!")
            return True
        except Exception as e:
            logger.error(f"Erreur dans reboot_scum: {e}", exc_info=True)
            return False

    def get_next_reboot_time(self):
        """Calcule le prochain horaire de reboot (synchrone)."""
        now = datetime.now()
        today = now.date()
        for reboot_time in self.reboot_times:
            next_reboot = datetime.combine(today, reboot_time)
            if next_reboot > now:
                return next_reboot
        tomorrow = today + timedelta(days=1)
        return datetime.combine(tomorrow, self.reboot_times[0])

    async def start_periodic_reboot(self):
        """Boucle infinie pour les reboots périodiques."""
        while True:
            try:
                now = datetime.now()
                next_reboot = self.get_next_reboot_time()
                time_until_reboot = (next_reboot - now).total_seconds()

                if time_until_reboot <= 0:
                    await self.reboot_scum()
                    await asyncio.sleep(60)  # Attend 1 minute avant de vérifier à nouveau
                else:
                    logger.info(f"Prochain reboot prévu à {next_reboot.strftime('%H:%M')}")
                    await asyncio.sleep(time_until_reboot)
            except asyncio.CancelledError:
                logger.info("Tâche de reboot annulée")
                break
            except Exception as e:
                logger.error(f"Erreur dans start_periodic_reboot: {e}", exc_info=True)
                await asyncio.sleep(60)  # Attend 1 minute en cas d'erreur

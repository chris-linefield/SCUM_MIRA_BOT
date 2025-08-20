import subprocess
import asyncio
import psutil
import pydirectinput
from datetime import datetime
from utils.logger import logger  # Assure-toi que ton module `logger` est configuré

# Désactive le fail-safe de pydirectinput (optionnel, pour éviter les interruptions)
pydirectinput.FAILSAFE = False

class SCUMManager:
    def __init__(self):
        self.steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
        self.scum_app_id = "513710"
        # Coordonnée du bouton "CONTINUER" (adaptée à ton setup multi-écrans)
        self.button_continue_pos = (-1676, 607)
        self.log_file = "scum_reboot.log"

    def is_scum_running(self):
        """Vérifie si SCUM est en cours d'exécution"""
        try:
            return "SCUM.exe" in [p.name() for p in psutil.process_iter()]
        except Exception as e:
            logger.error(f"Erreur vérification SCUM: {e}")
            return False

    def kill_scum(self):
        """Ferme SCUM"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == "SCUM.exe":
                    proc.kill()
            logger.info("SCUM fermé avec succès.")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture: {e}")
            return False

    async def launch_scum(self):
        """Lance SCUM et clique sur 'CONTINUER'"""
        try:
            # Lance SCUM via Steam
            subprocess.Popen([self.steam_path, "-applaunch", self.scum_app_id])
            logger.info("SCUM lancé. Attente de 45 secondes pour le chargement...")
            await asyncio.sleep(45)  # Temps pour que le jeu charge

            # Clique sur "CONTINUER"
            pydirectinput.moveTo(*self.button_continue_pos)
            pydirectinput.click()
            logger.info(f"Cliqué sur CONTINUER à {self.button_continue_pos}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du lancement: {e}")
            return False

    async def reboot_scum(self):
        """Redémarre SCUM et clique sur 'CONTINUER'"""
        try:
            logger.info("🔄 Redémarrage de SCUM...")
            if self.is_scum_running():
                logger.info("Fermeture de SCUM...")
                if not self.kill_scum():
                    return False
                await asyncio.sleep(5)  # Attend la fermeture

            logger.info("Relance de SCUM...")
            if not await self.launch_scum():
                return False

            # Log
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== Reboot SCUM - {datetime.now()} ===\n")
                f.write(f"Bouton CONTINUER cliqué à {self.button_continue_pos}\n")
                f.write("========================================\n")

            logger.info("SCUM relancé avec succès !")
            return True
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return False

# Exemple d'utilisation (standalone)
async def main():
    manager = SCUMManager()
    await manager.reboot_scum()

if __name__ == "__main__":
    asyncio.run(main())

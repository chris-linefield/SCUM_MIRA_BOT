# services/scum_reboot_service.py
import subprocess
import asyncio
import os
from datetime import datetime, time, timedelta
from utils.logger import logger

class SCUMRebootService:
    def __init__(self):
        self.reboot_batch_path = os.path.join(os.getcwd(), "reboot.bat")
        self.log_file = "scum_reboot.log"
        # Heures de reboot spécifiques
        self.reboot_times = [
            time(5, 0),   # 5h du matin
            time(9, 0),   # 9h du matin
            time(16, 0),  # 16h de l'après-midi
            time(21, 0),  # 21h du soir
            time(1, 0)    # 1h du matin
        ]
        self.last_reboot = None

    async def execute_reboot(self):
        """Exécute le script reboot.bat"""
        try:
            logger.info("🔄 Début de la procédure de redémarrage de SCUM...")

            # Vérifier que les fichiers batch existent
            if not os.path.exists(self.reboot_batch_path):
                logger.error(f"Fichier {self.reboot_batch_path} introuvable")
                return False

            # Exécuter le script batch
            result = subprocess.run(
                [self.reboot_batch_path],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Log des résultats
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== Reboot SCUM - {datetime.now()} ===\n")
                f.write(f"Sortie: {result.stdout}\n")
                f.write(f"Erreurs: {result.stderr}\n")
                f.write("========================================\n")

            logger.info("🔄 Procédure de redémarrage de SCUM terminée")
            self.last_reboot = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Erreur lors du redémarrage de SCUM: {str(e)}")
            return False

    def get_next_reboot_time(self):
        """Calcule le prochain horaire de reboot"""
        now = datetime.now()
        today = now.date()

        # Trouver le prochain horaire aujourd'hui
        for reboot_time in self.reboot_times:
            next_reboot = datetime.combine(today, reboot_time)
            if next_reboot > now:
                return next_reboot

        # Si tous les horaires sont passés aujourd'hui, prendre le premier de demain
        tomorrow = today + timedelta(days=1)
        return datetime.combine(tomorrow, self.reboot_times[0])

    async def start_periodic_reboot(self):
        """Démarre la boucle de redémarrage aux horaires spécifiques"""
        while True:
            try:
                # Calculer le prochain reboot
                next_reboot = self.get_next_reboot_time()
                time_until_reboot = (next_reboot - datetime.now()).total_seconds()

                logger.info(f"Prochain reboot prévu à {next_reboot.strftime('%H:%M')}")

                if time_until_reboot <= 0:
                    # C'est l'heure du reboot
                    await self.execute_reboot()
                    # Attendre 1 minute avant de vérifier le prochain horaire
                    await asyncio.sleep(60)
                else:
                    # Attendre jusqu'au prochain reboot
                    await asyncio.sleep(time_until_reboot)

            except Exception as e:
                logger.error(f"Erreur dans la boucle de reboot: {str(e)}")
                await asyncio.sleep(60)  # Attendre 1 minute avant de réessayer
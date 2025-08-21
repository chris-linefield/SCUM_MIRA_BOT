import subprocess
import asyncio
import os
import psutil
import time
from datetime import datetime, time, timedelta
from utils.logger import logger
from services.scum_service import send_scum_command

class SCUMManager:
    def __init__(self, bot):
        self.bot = bot
        self.status_channel_id = 1407804333281640508  # Canal pour le statut
        self.status_message = None
        self.reboot_times = [
            time(5, 0),   # 5h du matin
            time(9, 0),   # 9h du matin
            time(16, 0),  # 16h de l'après-midi
            time(21, 0),  # 21h du soir
            time(1, 0)    # 1h du matin
        ]
        self.last_reboot = None
        self.last_announce = None
        self.announce_sent = {str(t): False for t in self.reboot_times}

        # Configuration SCUM
        self.steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
        self.scum_app_id = "513710"
        self.server_ip = "172.0.0.1:2005"
        self.server_password = "MIRA072025"
        self.log_file = "scum_reboot.log"
        self.scum_config_path = os.path.expanduser("~/Documents/My Games/SCUM/Config/WindowsNoEditor/Engine.ini")

    def is_scum_running(self):
        """Vérifie si SCUM est en cours d'exécution"""
        try:
            return "SCUM.exe" in [p.name() for p in psutil.process_iter()]
        except Exception as e:
            logger.error(f"Erreur vérification SCUM: {e}")
            return False

    def kill_scum(self):
        """Tue tous les processus SCUM"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == "SCUM.exe":
                    proc.kill()
            logger.info("Processus SCUM tués avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de SCUM: {e}")
            return False

    def update_config_file(self):
        """Met à jour le fichier de configuration pour la connexion automatique"""
        try:
            config_dir = os.path.dirname(self.scum_config_path)
            os.makedirs(config_dir, exist_ok=True)

            config_content = ""
            if os.path.exists(self.scum_config_path):
                with open(self.scum_config_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()

            config_lines = config_content.split('\n')
            updated_lines = []
            session_section_found = False

            for line in config_lines:
                updated_lines.append(line)
                if "[/Script/Engine.GameSession]" in line:
                    session_section_found = True
                    updated_lines.append(f"PreferredServerIP={self.server_ip}")
                    updated_lines.append(f"PreferredServerPassword={self.server_password}")
                    updated_lines.append("bJoinOnStart=true")

            if not session_section_found:
                updated_lines.append("[/Script/Engine.GameSession]")
                updated_lines.append(f"PreferredServerIP={self.server_ip}")
                updated_lines.append(f"PreferredServerPassword={self.server_password}")
                updated_lines.append("bJoinOnStart=true")

            with open(self.scum_config_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_lines))

            logger.info(f"Fichier de configuration mis à jour: {self.scum_config_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur mise à jour configuration: {e}")
            return False

    def launch_scum(self):
        """Lance SCUM via Steam"""
        try:
            subprocess.Popen([
                self.steam_path,
                "-applaunch", self.scum_app_id,
                f"+connect {self.server_ip}",
                f"+password {self.server_password}"
            ])
            logger.info(f"SCUM lancé avec connexion à {self.server_ip}")
            return True
        except Exception as e:
            logger.error(f"Erreur lancement SCUM: {e}")
            return False

    async def send_reboot_announce(self, reboot_time):
        """Envoie une annonce 10 minutes avant le reboot"""
        try:
            if not self.is_scum_running():
                logger.warning("SCUM n'est pas en cours d'exécution, annonce annulée")
                return False

            success, result = await send_scum_command(
                "#Announce ⚠️ **ATTENTION** ⚠️ La tempête se lève ! Redémarrage du serveur dans 10 minutes !",
                0  # ID utilisateur 0 pour annonce globale
            )

            if success:
                logger.info(f"Annonce de reboot envoyée pour {reboot_time}")
                self.announce_sent[str(reboot_time)] = True
                return True
            else:
                logger.error(f"Échec de l'envoi de l'annonce: {result}")
                return False
        except Exception as e:
            logger.error(f"Erreur annonce reboot: {e}")
            return False

    async def reboot_scum(self):
        """Redémarre SCUM complètement"""
        try:
            logger.info("🔄 Début du redémarrage de SCUM...")

            # 1. Vérifier que SCUM est en cours d'exécution
            if not self.is_scum_running():
                logger.warning("SCUM n'est pas en cours d'exécution, reboot annulé")
                return False

            # 2. Fermer SCUM
            if not self.kill_scum():
                return False

            # Attendre que SCUM soit bien fermé
            time.sleep(10)

            # 3. Mettre à jour la configuration
            if not self.update_config_file():
                logger.error("Échec de la mise à jour de la configuration")
                return False

            # 4. Relancer SCUM
            if not self.launch_scum():
                return False

            # Log du reboot
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== Reboot SCUM - {datetime.now()} ===\n")
                f.write(f"Serveur: {self.server_ip}\n")
                f.write("Configuration mise à jour pour connexion automatique\n")
                f.write("========================================\n")

            logger.info("SCUM redémarré avec succès")
            self.last_reboot = datetime.now()

            # Réinitialiser le flag d'annonce
            current_time = datetime.now().time()
            for t in self.reboot_times:
                if t == current_time:
                    self.announce_sent[str(t)] = False
                    break

            return True
        except Exception as e:
            logger.error(f"Erreur lors du redémarrage: {str(e)}")
            return False

    def get_next_reboot_time(self):
        """Calcule le prochain horaire de reboot"""
        now = datetime.now()
        today = now.date()

        for reboot_time in self.reboot_times:
            next_reboot = datetime.combine(today, reboot_time)
            if next_reboot > now:
                return next_reboot

        tomorrow = today + timedelta(days=1)
        return datetime.combine(tomorrow, self.reboot_times[0])

    def get_announce_time(self, reboot_time):
        """Calcule l'heure d'annonce (10 min avant le reboot)"""
        reboot_datetime = datetime.combine(datetime.now().date(), reboot_time)
        return reboot_datetime - timedelta(minutes=10)

    async def check_and_reboot(self):
        """Vérifie et exécute le reboot si nécessaire"""
        try:
            now = datetime.now()

            # Vérifier si on doit envoyer une annonce (10 min avant)
            for reboot_time in self.reboot_times:
                announce_time = self.get_announce_time(reboot_time)

                if (now >= announce_time and
                    now <= announce_time + timedelta(seconds=60) and  # Fenêtre de 1 minute
                    not self.announce_sent[str(reboot_time)] and
                    self.is_scum_running()):

                    logger.info(f"Heure d'annonce atteinte pour {reboot_time}")
                    await self.send_reboot_announce(reboot_time)
                    break

            # Vérifier si c'est l'heure du reboot
            for reboot_time in self.reboot_times:
                reboot_datetime = datetime.combine(now.date(), reboot_time)

                if (now >= reboot_datetime and
                    now <= reboot_datetime + timedelta(seconds=60) and  # Fenêtre de 1 minute
                    self.announce_sent[str(reboot_time)] and
                    (not self.last_reboot or (now - self.last_reboot).total_seconds() > 3600)):

                    logger.info(f"Heure de reboot atteinte pour {reboot_time}")
                    success = await self.reboot_scum()
                    if success:
                        self.last_reboot = now
                    break

        except Exception as e:
            logger.error(f"Erreur vérification reboot: {e}")

    async def start_periodic_check(self):
        """Démarre la vérification périodique toutes les minutes"""
        while True:
            try:
                await self.check_and_reboot()
                await asyncio.sleep(60)  # Vérifier toutes les minutes
            except Exception as e:
                logger.error(f"Erreur dans la boucle de vérification: {e}")
                await asyncio.sleep(60)

    async def update_status_message(self, status):
        """Met à jour le message de statut dans le canal dédié"""
        try:
            channel = self.bot.get_channel(self.status_channel_id)
            if channel:
                if self.status_message:
                    await self.status_message.edit(content=f"🔴 **Statut du Bot:**\n{status}\nDernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
                else:
                    self.status_message = await channel.send(f"🔴 **Statut du Bot:**\n{status}\nDernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            logger.error(f"Erreur mise à jour statut: {e}")
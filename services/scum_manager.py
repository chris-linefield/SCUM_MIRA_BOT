import subprocess
import asyncio
import os
import psutil
import time
import pyautogui
from datetime import datetime, time, timedelta
from utils.logger import logger

class SCUMManager:
    def __init__(self):
        # Configuration des horaires de reboot
        self.reboot_times = [
            time(5, 0),   # 5h du matin
            time(9, 0),   # 9h du matin
            time(16, 0),  # 16h de l'après-midi
            time(21, 0),  # 21h du soir
            time(1, 0)    # 1h du matin
        ]
        self.last_reboot = None
        self.log_file = "scum_reboot.log"
        # Configuration SCUM
        self.steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
        self.scum_app_id = "513710"
        self.server_ip = "176.57.173.98:28702"
        self.server_password = "MIRA072025"
        # Coordonnées des éléments à cliquer (à adapter selon ta résolution)
        self.button_continue_pos = (960, 200)  # Bouton "CONTINUER"
        self.join_server_pos = (960, 300)      # Bouton "Rejoindre un serveur"
        self.ip_field_pos = (960, 350)         # Champ IP
        self.password_field_pos = (960, 400)   # Champ mot de passe
        self.connect_button_pos = (960, 450)   # Bouton "Se connecter"
        # Chemin vers le fichier de configuration de SCUM
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
            if "[/Script/Engine.GameSession]" not in config_content:
                config_content += "\n[/Script/Engine.GameSession]\n"
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
        """Lance SCUM via Steam et automatise la connexion"""
        try:
            if not self.update_config_file():
                logger.error("Échec de la mise à jour de la configuration")
                return False
            subprocess.Popen([self.steam_path, "-applaunch", self.scum_app_id])
            logger.info(f"SCUM lancé. Attente de 45 secondes pour le chargement...")
            time.sleep(45)  # Temps pour que le jeu charge complètement

            # Cliquer sur "CONTINUER"
            pyautogui.click(self.button_continue_pos)
            time.sleep(3)
            logger.info("Cliqué sur CONTINUER")

            # Cliquer sur "Rejoindre un serveur"
            pyautogui.click(self.join_server_pos)
            time.sleep(3)
            logger.info("Cliqué sur Rejoindre un serveur")

            # Entrer l'IP du serveur
            pyautogui.click(self.ip_field_pos)
            pyautogui.write(self.server_ip)
            time.sleep(1)
            logger.info(f"IP entrée: {self.server_ip}")

            # Entrer le mot de passe
            pyautogui.click(self.password_field_pos)
            pyautogui.write(self.server_password)
            time.sleep(1)
            logger.info("Mot de passe entré")

            # Cliquer sur "Se connecter"
            pyautogui.click(self.connect_button_pos)
            logger.info("Connexion au serveur initiée")

            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'automatisation: {e}")
            return False

    async def reboot_scum(self):
        """Redémarre SCUM complètement"""
        try:
            logger.info("🔄 Début du redémarrage de SCUM...")
            if self.is_scum_running():
                logger.info("Fermeture de SCUM en cours...")
                if not self.kill_scum():
                    logger.error("Échec de la fermeture de SCUM")
                    return False
                time.sleep(10)
            if not self.update_config_file():
                logger.error("Échec de la mise à jour de la configuration")
                return False
            logger.info("Relance de SCUM...")
            if not self.launch_scum():
                logger.error("Échec du lancement de SCUM")
                return False
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== Reboot SCUM - {datetime.now()} ===\n")
                f.write(f"Serveur: {self.server_ip}\n")
                f.write(f"Mot de passe: {self.server_password}\n")
                f.write("Connexion automatique effectuée\n")
                f.write("========================================\n")
            logger.info("SCUM redémarré avec succès")
            self.last_reboot = datetime.now()
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

    async def start_periodic_reboot(self):
        """Démarre la boucle de redémarrage aux horaires spécifiques"""
        while True:
            try:
                next_reboot = self.get_next_reboot_time()
                time_until_reboot = (next_reboot - datetime.now()).total_seconds()
                logger.info(f"Prochain reboot prévu à {next_reboot.strftime('%H:%M')}")
                if time_until_reboot <= 0:
                    await self.reboot_scum()
                    await asyncio.sleep(60)
                else:
                    await asyncio.sleep(time_until_reboot)
            except Exception as e:
                logger.error(f"Erreur dans la boucle de reboot: {str(e)}")
                await asyncio.sleep(60)

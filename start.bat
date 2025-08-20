@echo off
:: Script pour démarrer SCUM et se connecter au serveur MIRA

:: Chemin vers SCUM (à adapter si nécessaire)
set SCUM_PATH="C:\Program Files (x86)\Steam\steamapps\common\SCUM\Binaries\Win64\SCUM.exe"

:: Paramètres de connexion
set SERVER_IP=176.57.173.98:28702
set SERVER_PASSWORD=MIRA072025

echo [SCUM] Démarrage du client SCUM avec connexion automatique au serveur %SERVER_IP%...
start "" "%SCUM_PATH%" -log -NoSplash -server=%SERVER_IP% -password=%SERVER_PASSWORD%

:: Attendre que SCUM démarre (30 secondes)
timeout /t 30 /nobreak >nul

exit

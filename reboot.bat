@echo off
:: Script pour redémarrer SCUM et se reconnecter au serveur

:: 1. Tuer le processus SCUM.exe
echo [SCUM] Fermeture du client SCUM en cours...
taskkill /f /im SCUM.exe >nul 2>&1
timeout /t 5 /nobreak >nul

:: 2. Vérifier que le processus est bien terminé
taskkill /f /im SCUM.exe >nul 2>&1
timeout /t 5 /nobreak >nul

:: 3. Lancer le script de démarrage
echo [SCUM] Redémarrage du client SCUM...
start "" "start.bat"

exit

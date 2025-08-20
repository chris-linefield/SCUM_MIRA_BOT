@echo off
:: Script pour redémarrer SCUM

:: 1. Tuer le processus SCUM.exe
echo [SCUM] Fermeture du client SCUM en cours...
taskkill /f /im SCUM.exe >nul 2>&1
timeout /t 5 /nobreak >nul

:: 2. Vérifier que le processus est bien terminé
taskkill /f /im SCUM.exe >nul 2>&1
timeout /t 5 /nobreak >nul

:: 3. Lancer start.bat avec chemin complet
echo [SCUM] Redémarrage du client SCUM...
cd /d "%~dp0"
call "start.bat"

exit

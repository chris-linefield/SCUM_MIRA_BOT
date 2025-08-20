@echo off
:loop
python main.py
if %errorlevel% neq 0 (
    echo Erreur détectée, redémarrage dans 5 secondes...
    timeout /t 5
)
goto loop

"C:\Program Files (x86)\Steam\steamapps\common\SCUM\SCUM\Binaries\Win64\SCUM.exe" -log -NoSplashScreen -serveraddr=176.57.173.98 -serverport=28702 -password=MIRA072025

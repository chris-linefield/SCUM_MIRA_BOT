@echo off
:loop
python main.py
if %errorlevel% neq 0 (
    echo Erreur détectée, redémarrage dans 5 secondes...
    timeout /t 5
)
goto loop

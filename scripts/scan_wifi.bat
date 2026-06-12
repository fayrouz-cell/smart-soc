@echo off
REM Script pour scanner le trafic WiFi Oreedo
REM Nécessite des privilèges administrateur

echo ========================================
echo   Scanner le trafic WiFi Oreedo
echo ========================================
echo.

REM Vérifier les privilèges administrateur
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERREUR] Ce script doit etre execute en tant qu'administrateur!
    echo.
    echo Veuillez faire un clic droit sur ce fichier et selectionner
    echo "Executer en tant qu'administrateur"
    echo.
    pause
    exit /b 1
)

echo [OK] Privileges administrateur detectes
echo.

REM Aller dans le répertoire du projet
cd /d "%~dp0\.."

REM Lister les interfaces disponibles
echo Liste des interfaces disponibles:
echo.
python tools/list_interfaces.py
echo.

REM Demander l'interface à utiliser
set /p INTERFACE="Entrez le nom de l'interface WiFi (ou appuyez sur Entree pour auto-detection): "

if "%INTERFACE%"=="" (
    echo.
    echo Demarrage avec auto-detection de l'interface...
    python main.py --start --mode live
) else (
    echo.
    echo Demarrage de la capture sur l'interface: %INTERFACE%
    python main.py --start --mode live --interface "%INTERFACE%"
)

echo.
echo Capture terminee.
pause


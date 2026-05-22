@echo off
setlocal

pushd "%~dp0"
set EXIT_CODE=0

echo.
echo === PyRenamer ===
echo Inserisci il percorso della cartella/file da rinominare.
set /p TARGET_PATH=Path: 

if "%TARGET_PATH%"=="" (
    echo.
    echo Errore: nessun percorso inserito.
    set EXIT_CODE=1
    goto :end
)

echo.
echo --- Anteprima rinomina (--dry-run) ---
python rename.py "%TARGET_PATH%" --dry-run
if errorlevel 1 (
    echo.
    echo Errore durante il dry-run. Operazione annullata.
    set EXIT_CODE=1
    goto :end
)

echo.
set /p CONFIRM=Confermi la rinomina reale? [INVIO=SI, N=No]: 
if /I "%CONFIRM%"=="N" (
    echo.
    echo Operazione annullata.
    set EXIT_CODE=0
    goto :end
)
if /I "%CONFIRM%"=="NO" (
    echo.
    echo Operazione annullata.
    set EXIT_CODE=0
    goto :end
)

echo.
echo --- Rinomina in corso ---
python rename.py "%TARGET_PATH%"
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% EQU 0 (
    echo Completato.
) else (
    echo Terminato con errori. Codice: %EXIT_CODE%
)

:end
echo.
pause
popd
exit /b %EXIT_CODE%

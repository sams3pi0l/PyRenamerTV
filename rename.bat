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

:confirm
echo.
set "CONFIRM="
set "RESULT_INDEX=1"
set /p "CONFIRM=Confermi la rinomina reale? [INVIO=primo, 1-5=risultato, N=No]: "
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
if "%CONFIRM%"=="" goto :rename
if "%CONFIRM%"=="1" goto :rename
if "%CONFIRM%"=="2" (
    set "RESULT_INDEX=2"
    goto :rename
)
if "%CONFIRM%"=="3" (
    set "RESULT_INDEX=3"
    goto :rename
)
if "%CONFIRM%"=="4" (
    set "RESULT_INDEX=4"
    goto :rename
)
if "%CONFIRM%"=="5" (
    set "RESULT_INDEX=5"
    goto :rename
)
echo Scelta non valida. Premi Invio, digita un numero da 1 a 5 oppure N.
goto :confirm

:rename
echo.
echo --- Rinomina in corso ---
python rename.py "%TARGET_PATH%" --result %RESULT_INDEX%
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

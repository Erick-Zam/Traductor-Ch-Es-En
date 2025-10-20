@echo off
echo ========================================
echo   TRADUCTOR CHINO - BUILD SCRIPT
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Instala Python 3.8+ primero.
    pause
    exit /b 1
)

echo [2/4] Instalando dependencias...
pip install pyinstaller customtkinter deep-translator pyttsx3 pypinyin CTkTable

echo [3/4] Creando ejecutable optimizado...
echo Esto puede tomar 2-3 minutos...

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "TraductorChino" ^
    --icon=icon.ico ^
    --add-data "README.md;." ^
    --hidden-import "customtkinter" ^
    --hidden-import "CTkTable" ^
    --hidden-import "pypinyin" ^
    --hidden-import "deep_translator.google" ^
    --hidden-import "pyttsx3.drivers" ^
    --hidden-import "pyttsx3.drivers.sapi5" ^
    --optimize 2 ^
    --strip ^
    main.py

echo [4/4] Verificando resultado...
if exist "dist\TraductorChino.exe" (
    echo.
    echo ========================================
    echo   BUILD COMPLETADO EXITOSAMENTE!
    echo ========================================
    echo.
    echo Archivo creado: dist\TraductorChino.exe
    
    for %%I in ("dist\TraductorChino.exe") do (
        set size=%%~zI
        set /a sizeMB=!size!/1024/1024
    )
    
    echo Tamaño: aproximadamente 35-40 MB
    echo.
    echo Para distribuir:
    echo 1. Copia TraductorChino.exe a cualquier PC Windows
    echo 2. No requiere Python instalado
    echo 3. Requiere conexion a internet para traducir
    echo.
    echo Probando ejecutable...
    start "" "dist\TraductorChino.exe"
) else (
    echo ERROR: No se pudo crear el ejecutable.
    echo Revisa los errores arriba.
)

echo.
echo Presiona cualquier tecla para continuar...
pause >nul
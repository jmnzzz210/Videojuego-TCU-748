@echo off
REM Proyecto: Ecos en la Estación
REM Autores: Marvin Coto Jiménez y Brandon Jiménez Campos
REM Script para ejecutar el juego en Windows

cd /d "%~dp0"

REM Verificar si las librerias estan instaladas
python -c "import sounddevice, numpy, scipy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Instalando dependencias necesarias...
    pip install -r requirements.txt
    echo.
)

python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocurrio un error al ejecutar el juego.
    echo Verifica que Python este instalado y en el PATH.
    pause
)

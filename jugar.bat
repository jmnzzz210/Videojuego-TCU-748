@echo off
REM Proyecto: Ecos en la Estación
REM Autores: Marvin Coto Jiménez y Brandon Jiménez Campos
REM Script para ejecutar el juego en Windows

cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocurrio un error al ejecutar el juego.
    echo Asegurate de tener instaladas las dependencias ejecutando:
    echo pip install -r requirements.txt
    echo.
    pause
)


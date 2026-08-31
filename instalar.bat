@echo off
REM Proyecto: Ecos en la Estación
REM Autores: Marvin Coto Jiménez y Brandon Jiménez Campos
REM Script para instalar dependencias en Windows con doble clic

echo ======================================================
echo   ECOS EN LA ESTACION - INSTALADOR DE DEPENDENCIAS
echo ======================================================
echo.
echo Instalando sounddevice, numpy y scipy...
pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================
    echo  [OK] Dependencias instaladas con exito!
    echo  Ya puedes hacer doble clic en jugar.bat para jugar.
    echo ======================================================
) else (
    echo.
    echo ======================================================
    echo  [ERROR] Ocurrio un error al instalar.
    echo  Verifica que Python y pip esten instalados y en el PATH.
    echo ======================================================
)
echo.
pause


"""
Proyecto: Ecos en la Estación - Punto de Entrada
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Archivo principal que ajusta la ruta de importaciones y lanza la interfaz gráfica.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al path de Python para evitar errores de importación
GAME_ROOT = Path(__file__).resolve().parent
if str(GAME_ROOT) not in sys.path:
    sys.path.insert(0, str(GAME_ROOT))

from ui.visualizer import GameUI, _TK_AVAILABLE

if __name__ == "__main__":
    if not _TK_AVAILABLE:
        print("Error: tkinter no está disponible. Instálalo con: sudo apt-get install python3-tk")
        sys.exit(1)

    try:
        app = GameUI()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)

"""
Proyecto: Ecos en la Estación - Configuración Global
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Archivo de constantes y configuraciones globales para el juego. Incluye
frecuencia de muestreo, límites del mapa, parámetros de movimiento del
jugador y constantes acústicas.
"""

from pathlib import Path

# Parámetros básicos de audio
SAMPLE_RATE: int = 44100
CHANNELS: int = 2

# Rutas de archivos y carpetas del proyecto
BASE_DIR: Path = Path(__file__).resolve().parent
AUDIO_DIR: Path = BASE_DIR / "audio"
ASSETS_DIR: Path = AUDIO_DIR / "assets"

# Límites del cuarto en metros (el centro inicial es 0,0)
ROOM_X_MIN: float = -4.0
ROOM_X_MAX: float = 4.0
ROOM_Y_MIN: float = -2.0
ROOM_Y_MAX: float = 5.0

# Movimiento y posición inicial del jugador
MOVE_STEP: float = 1.0          # Avance por paso (en metros)
TURN_STEP: float = 90.0         # Giro por pulsación (en grados, 90° para direcciones cardinales)
START_X: float = 0.0            # Coordenada X inicial
START_Y: float = 0.0            # Coordenada Y inicial
START_FACING_DEG: float = 0.0   # Orientación inicial (0° mira hacia el norte, eje +Y)

# Distancia y ángulo máximo para poder interactuar con objetos
INTERACTION_DISTANCE: float = 1.3        # Distancia máxima de interacción en metros
INTERACTION_ANGLE_THRESHOLD: float = 40.0 # Tolerancia angular en grados para estar "de frente"

# Parámetros físicos para el cálculo de audio 3D y HRTF
SPEED_OF_SOUND: float = 343.0            # Velocidad del sonido en m/s
HEAD_RADIUS: float = 0.0875              # Radio aproximado de la cabeza en metros
ROOM_REVERB_SIZE: float = 5.0            # Tamaño de la habitación para la reverberación

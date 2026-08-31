"""
Proyecto: Ecos en la Estación - Módulo de Audio
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Paquete de procesamiento de audio. Expone el motor de espacialización HRTF
y el generador de sintetización de sonidos.
"""

from .hrtf_engine import HRTFEngine
from .sound_generator import SoundGenerator

__all__ = ["HRTFEngine", "SoundGenerator"]

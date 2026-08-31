"""
Proyecto: Ecos en la Estación - Narrador y Retroalimentación
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Sistema de mensajes e indicaciones por consola y reproducción de efectos de sonido
prioritarios (retroalimentación de voz, pasos, errores y avisos de interfaz).
"""

import time
import numpy as np

from config import SAMPLE_RATE
from audio.mixer import get_mixer


class Narrator:
    """
    Clase para emisión de mensajes de texto en pantalla y eventos sonoros.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE, enable_audio: bool = True):
        self.sample_rate = sample_rate
        self.enable_audio = enable_audio
        self._mixer = get_mixer(sample_rate)

    def print_banner(self, title: str):
        """Imprime un recuadro decorativo con un título."""
        width = 54
        print("\n" + "╔" + "═" * (width - 2) + "╗")
        print(f"║ {title.center(width - 4)} ║")
        print("╚" + "═" * (width - 2) + "╝")

    def narrate(self, message: str, delay_after: float = 0.2):
        """Muestra un texto narrativo en pantalla."""
        print(f"\n{message}")
        time.sleep(delay_after)

    def play_sound(self, audio: np.ndarray, wait: bool = False):
        """Reproduce un efecto de sonido utilizando el mezclador de audio."""
        if not self.enable_audio:
            return
        self._mixer.play_event(audio, wait=wait)

    def announce_status(self, player_desc: str, compass: str, objects_info: list[str]):
        """Imprime el estado de orientación y las fuentes de sonido alrededor del jugador."""
        print("\n" + "─" * 48)
        print(f"Posición: {player_desc} | Mirando: {compass}")
        print("Fuentes de sonido perceptibles:")
        for info in objects_info:
            print(f"   • {info}")
        print("─" * 48)

"""
Proyecto: Ecos en la Estación - Mezclador de Audio
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Módulo de control de audio centralizado. Implementa una clase singleton con
bloqueo de hilos (threading.Lock) para gestionar la reproducción de sonidos
de eventos y sonidos ambientales usando sounddevice sin conflictos entre hilos.
"""

import threading
import time
from typing import Optional
import numpy as np

try:
    import sounddevice as sd
    _SD_AVAILABLE = True
except ImportError:
    sd = None
    _SD_AVAILABLE = False

from config import SAMPLE_RATE


class AudioMixer:
    """
    Gestiona las llamadas a sounddevice garantizando acceso thread-safe.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._lock = threading.Lock()
        self._event_until: float = 0.0   # Controla la duración del evento activo
        self._available = _SD_AVAILABLE

    def play_event(self, audio: np.ndarray, wait: bool = False):
        """
        Reproduce un sonido prioritario de evento (pasos, interacciones, etc).
        """
        if not self._available or sd is None or len(audio) == 0:
            return

        # Convertir a estéreo si viene en formato mono
        if audio.ndim == 1:
            audio = np.column_stack((audio, audio))

        duration = len(audio) / self.sample_rate
        with self._lock:
            try:
                sd.stop()
                sd.play(audio, self.sample_rate)
                self._event_until = time.monotonic() + duration
            except Exception as e:
                print(f"Error reproduciendo evento: {e}")

        if wait:
            try:
                sd.wait()
            except Exception:
                pass

    def play_ambient(self, audio: np.ndarray):
        """
        Reproduce un sonido ambiental secundario si no hay un evento activo.
        """
        if not self._available or sd is None or len(audio) == 0:
            return

        # Convertir a estéreo si viene en formato mono
        if audio.ndim == 1:
            audio = np.column_stack((audio, audio))

        # Evitar interrumpir un evento de mayor prioridad
        if time.monotonic() < self._event_until:
            return

        # Intentar obtener el cerrojo sin bloquear el hilo principal
        acquired = self._lock.acquire(blocking=False)
        if not acquired:
            return

        try:
            sd.stop()
            sd.play(audio, self.sample_rate)
            self._event_until = 0.0
        except Exception as e:
            print(f"Error reproduciendo ambiente: {e}")
        finally:
            self._lock.release()

    def stop_all(self):
        """
        Detiene cualquier reproducción en curso.
        """
        if not self._available or sd is None:
            return
        try:
            sd.stop()
        except Exception:
            pass

    def close(self):
        """
        Cierra y libera los recursos de audio al salir del juego.
        """
        self.stop_all()


# Instancia única del mezclador compartida en todo el sistema
_mixer: Optional[AudioMixer] = None


def get_mixer(sample_rate: int = SAMPLE_RATE) -> AudioMixer:
    """
    Retorna la instancia global del mezclador de audio.
    """
    global _mixer
    if _mixer is None:
        _mixer = AudioMixer(sample_rate)
    return _mixer

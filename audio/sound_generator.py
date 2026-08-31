"""
Proyecto: Ecos en la Estación - Generador de Sonidos y Assets
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Sintetizador de señales de audio y manejador de archivos WAV. Genera
sonidos sintéticos para los objetos del juego (teléfono, radio, pisadas,
choque con paredes, cerradura) y permite guardarlos o cargarlos de disco.
"""

import os
import wave
from pathlib import Path
from typing import Optional

import numpy as np
from scipy import signal

from config import SAMPLE_RATE, ASSETS_DIR


class SoundGenerator:
    """
    Clase para la sintetización matemática de formas de onda.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate

    def _apply_envelope(self, wave_arr: np.ndarray, shape: str = "smooth") -> np.ndarray:
        """
        Aplica un suavizado al inicio y final de la onda para evitar clics acústicos.
        """
        n = len(wave_arr)
        if n == 0:
            return wave_arr

        if shape == "smooth":
            fade = int(n * 0.1)
            env = np.ones(n, dtype=np.float32)
            if fade > 0:
                env[:fade] = np.linspace(0, 1, fade)
                env[-fade:] = np.linspace(1, 0, fade)
        elif shape == "sharp":
            fade_in = int(n * 0.05)
            fade_out = int(n * 0.2)
            env = np.ones(n, dtype=np.float32)
            if fade_in > 0:
                env[:fade_in] = np.linspace(0, 1, fade_in)
            if fade_out > 0:
                env[-fade_out:] = np.linspace(1, 0, fade_out)
        else:
            env = np.ones(n, dtype=np.float32)

        return (wave_arr * env).astype(np.float32)

    def tone(self, frequency: float = 440.0, duration: float = 0.5, envelope: str = "smooth") -> np.ndarray:
        """Genera una senoidal pura."""
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        w = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        return self._apply_envelope(w, envelope)

    def beep(self, frequency: float = 880.0, duration: float = 0.2) -> np.ndarray:
        """Genera un tono breve de orientación."""
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        w = 0.7 * np.sin(2 * np.pi * frequency * t) + 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        return self._apply_envelope(w.astype(np.float32), "sharp")

    def ping(self, frequency: float = 1200.0, duration: float = 0.35) -> np.ndarray:
        """Genera un pulso resonante tipo ecolocalización."""
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        w = (np.sin(2 * np.pi * frequency * t) * np.exp(-t * 10) +
             0.5 * np.sin(2 * np.pi * frequency * 2.756 * t) * np.exp(-t * 14) +
             0.3 * np.sin(2 * np.pi * frequency * 5.404 * t) * np.exp(-t * 18))
        max_val = np.max(np.abs(w)) + 1e-10
        return (w / max_val).astype(np.float32)

    def footstep(self, duration: float = 0.12) -> np.ndarray:
        """Genera el efecto de sonido de un paso sobre el suelo."""
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n)
        noise = np.random.randn(n) * 0.6
        b, a = signal.butter(4, [100.0 / (self.sr / 2), 700.0 / (self.sr / 2)], btype="band")
        filtered = signal.lfilter(b, a, noise)
        env = np.exp(-t * 30)
        w = filtered * env
        max_val = np.max(np.abs(w)) + 1e-10
        return (w / max_val * 0.8).astype(np.float32)

    def wall_bump(self, duration: float = 0.20) -> np.ndarray:
        """Genera el efecto de un choque contra la pared."""
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        w = np.sin(2 * np.pi * 80 * t) * np.exp(-t * 20)
        noise = np.random.randn(len(t)) * 0.15 * np.exp(-t * 35)
        total = w + noise
        max_val = np.max(np.abs(total)) + 1e-10
        return (total / max_val * 0.85).astype(np.float32)

    def door_locked(self, duration: float = 0.45) -> np.ndarray:
        """Genera el sonido de puerta bloqueada (golpe metálico y zumbido)."""
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        clunk = (np.sin(2 * np.pi * 120 * t) * np.exp(-t * 12) +
                 0.5 * np.sin(2 * np.pi * 240 * t) * np.exp(-t * 18))
        buzz_env = np.exp(-t * 8) * (t > 0.05)
        buzz = 0.3 * np.sin(2 * np.pi * 60 * t) * buzz_env
        buzz += 0.15 * np.sin(2 * np.pi * 120 * t) * buzz_env
        total = clunk + buzz
        max_val = np.max(np.abs(total)) + 1e-10
        return (total / max_val * 0.9).astype(np.float32)

    def wrong_direction(self, duration: float = 0.18) -> np.ndarray:
        """Genera tono corto de orientación incorrecta."""
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        freq = 700 - 300 * t / duration
        phase = 2 * np.pi * np.cumsum(freq) / self.sr
        w = np.sin(phase) * np.exp(-t * 25)
        max_val = np.max(np.abs(w)) + 1e-10
        return (w / max_val * 0.7).astype(np.float32)

    def door_hum(self, duration: float = 1.0) -> np.ndarray:
        """Genera zumbido eléctrico continuo para la puerta cuando está lista para abrir."""
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        hum = (0.6 * np.sin(2 * np.pi * 60 * t) +
               0.3 * np.sin(2 * np.pi * 120 * t) +
               0.1 * np.sin(2 * np.pi * 180 * t))
        pulse = 0.7 + 0.3 * np.sin(2 * np.pi * 1.2 * t)
        noise = np.random.randn(len(t)) * 0.04
        from scipy import signal as _sig
        b, a = _sig.butter(2, 200.0 / (self.sr / 2), btype="low")
        noise = _sig.lfilter(b, a, noise)
        total = (hum * pulse + noise)
        max_val = np.max(np.abs(total)) + 1e-10
        return (total / max_val * 0.65).astype(np.float32)

    def telephone_ring(self, duration: float = 1.0) -> np.ndarray:
        """Genera el timbre de un teléfono de escritorio."""
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        dual = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.5 * np.sin(2 * np.pi * 480 * t)
        tremolo = 0.6 + 0.4 * np.sin(2 * np.pi * 20 * t)
        pulse = (np.sin(2 * np.pi * 2.5 * t) > 0).astype(float)
        w = dual * tremolo * pulse
        return self._apply_envelope(w.astype(np.float32), "smooth")

    def radio_broadcast(self, duration: float = 1.2) -> np.ndarray:
        """Genera sonido de transmisión de radio con estática."""
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n)
        noise = np.random.randn(n) * 0.3
        b, a = signal.butter(3, [300.0 / (self.sr / 2), 3400.0 / (self.sr / 2)], btype="band")
        filtered_noise = signal.lfilter(b, a, noise)
        melody = 0.25 * (np.sin(2 * np.pi * 523.25 * t) + 0.5 * np.sin(2 * np.pi * 659.25 * t))
        w = filtered_noise + melody
        max_val = np.max(np.abs(w)) + 1e-10
        return self._apply_envelope((w / max_val * 0.7).astype(np.float32), "smooth")

    def door_creak(self, duration: float = 0.8) -> np.ndarray:
        """Genera el chirrido de apertura de la puerta."""
        n = int(self.sr * duration)
        t = np.linspace(0, duration, n)
        freq = 300 + 400 * t + 80 * np.sin(2 * np.pi * 35 * t)
        phase = 2 * np.pi * np.cumsum(freq) / self.sr
        creak = 0.5 * np.sin(phase) * (1 - t / duration)
        click = np.zeros(n)
        if n > 200:
            click[-200:] = np.random.randn(200) * np.linspace(1, 0, 200)
        total = creak + click
        max_val = np.max(np.abs(total)) + 1e-10
        return (total / max_val * 0.8).astype(np.float32)

    def confirmation(self) -> np.ndarray:
        """Genera tono de confirmación de interacción exitosa."""
        duration = 0.35
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        n_half = len(t) // 2
        w1 = np.sin(2 * np.pi * 587.33 * t[:n_half])
        w2 = np.sin(2 * np.pi * 880.00 * t[n_half:])
        w = np.concatenate([w1, w2])
        return self._apply_envelope(w.astype(np.float32), "sharp")

    def error(self) -> np.ndarray:
        """Genera tono de error."""
        duration = 0.25
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        w = np.sin(2 * np.pi * 180 * t) * (np.sin(2 * np.pi * 12 * t) > 0)
        return self._apply_envelope(w.astype(np.float32), "sharp")


def save_wav(filename: Path | str, mono_data: np.ndarray, sample_rate: int = SAMPLE_RATE) -> Path:
    """Guarda un arreglo de audio mono en un archivo en formato WAV PCM de 16 bits."""
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    clipped = np.clip(mono_data, -1.0, 1.0)
    int16_data = (clipped * 32767).astype(np.int16)

    with wave.open(str(filepath), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int16_data.tobytes())

    return filepath


def load_wav(filename: Path | str, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Carga un archivo WAV y convierte su contenido en un arreglo flotante entre -1.0 y 1.0."""
    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"No se encontró el archivo de audio: {filepath}")

    with wave.open(str(filepath), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        frames = wf.readframes(n_frames)

    if sampwidth == 2:
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 1:
        audio = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        audio = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0

    if n_channels > 1:
        audio = audio.reshape(-1, n_channels).mean(axis=1)

    if framerate != sample_rate and len(audio) > 0:
        new_len = int(len(audio) * sample_rate / framerate)
        audio = signal.resample(audio, new_len)

    return audio.astype(np.float32)


def generate_default_assets(assets_dir: Path = ASSETS_DIR):
    """
    Crea los archivos WAV predeterminados en la carpeta de recursos si aún no existen.
    """
    assets_dir.mkdir(parents=True, exist_ok=True)
    gen = SoundGenerator()

    sound_map = {
        "telefono.wav":         gen.telephone_ring(1.0),
        "radio.wav":            gen.radio_broadcast(1.2),
        "puerta_abrir.wav":     gen.door_creak(0.8),
        "pasos.wav":            gen.footstep(0.12),
        "confirmacion.wav":     gen.confirmation(),
        "error.wav":            gen.error(),
        "golpe_pared.wav":      gen.wall_bump(0.20),
        "puerta_bloqueada.wav": gen.door_locked(0.45),
        "orientacion_mal.wav":  gen.wrong_direction(0.18),
        "puerta_hum.wav":       gen.door_hum(1.0),
    }

    for name, data in sound_map.items():
        out_path = assets_dir / name
        if not out_path.exists() or name == "golpe_pared.wav":
            save_wav(out_path, data)

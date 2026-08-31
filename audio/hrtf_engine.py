"""
Proyecto: Ecos en la Estación - Motor HRTF
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Motor de procesamiento de audio espacial 3D basado en funciones de transferencia
relacionadas con la cabeza (HRTF). Aplica retardo interaural de tiempo (ITD),
diferencia interaural de nivel (ILD), filtrado espectral de pabellón auricular (Pinna),
atenuación por distancia y reverberación de sala.
"""

import numpy as np
from scipy import signal
from typing import Optional

from config import (
    SAMPLE_RATE,
    SPEED_OF_SOUND,
    HEAD_RADIUS,
    ROOM_REVERB_SIZE,
)


class HRTFEngine:
    """
    Clase encargada de la espacialización de audio estéreo.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE,
                 head_radius: float = HEAD_RADIUS,
                 speed_of_sound: float = SPEED_OF_SOUND):
        self.sample_rate = sample_rate
        self.head_radius = head_radius
        self.speed_of_sound = speed_of_sound

    def compute_itd(self, azimuth_deg: float) -> float:
        """
        Calcula la diferencia de tiempo entre oídos (ITD) en segundos usando el modelo de Woodworth.
        """
        az_rad = np.radians(azimuth_deg)
        return (self.head_radius / self.speed_of_sound) * (az_rad + np.sin(az_rad))

    def compute_ild(self, azimuth_deg: float, frequency_hz: float = 1000.0) -> float:
        """
        Calcula la diferencia de intensidad sonora entre oídos (ILD) en decibelios.
        """
        az_rad = np.radians(azimuth_deg)
        freq_factor = min(frequency_hz / 1000.0, 3.0)
        return 20.0 * np.sin(az_rad) * freq_factor

    def design_pinna_filter(self, elevation_deg: float, ear: str) -> np.ndarray:
        """
        Genera el filtro FIR que emula las deformaciones producidas por la oreja humana según la elevación.
        """
        n_taps = 128
        freq_response = np.ones(n_taps // 2 + 1, dtype=complex)
        freqs = np.linspace(0, self.sample_rate / 2, n_taps // 2 + 1)
        el_rad = np.radians(elevation_deg)

        for i, f in enumerate(freqs):
            if f == 0:
                continue

            # Muesca espectral según elevación
            notch_freq = 8000.0 + 2000.0 * np.sin(el_rad)
            notch_q = 3.0
            dist_from_notch = abs(f - notch_freq) / notch_freq
            notch_depth = np.exp(-dist_from_notch ** 2 * notch_q) * 0.6

            # Realce de presencia
            presence_freq = 4000.0 + 1000.0 * np.cos(el_rad)
            dist_presence = abs(f - presence_freq) / presence_freq
            presence_gain = np.exp(-dist_presence ** 2 * 2.0) * 0.3

            freq_response[i] *= (1.0 - notch_depth + presence_gain)

            if ear == "left":
                freq_response[i] *= (1.0 + 0.1 * np.cos(el_rad))

        # Transformada inversa para obtener respuesta al impulso en el tiempo
        h = np.real(np.fft.irfft(freq_response))
        h *= np.hanning(len(h))
        h /= np.sum(np.abs(h)) + 1e-10
        return h

    def apply_distance_model(self, audio: np.ndarray, distance_m: float) -> np.ndarray:
        """
        Aplica la atenuación de volumen por distancia e incluye filtrado pasabajos por absorción del aire.
        """
        ref_distance = 1.0
        distance_m = max(distance_m, 0.1)

        # Ganancia inversamente proporcional a la distancia
        gain = ref_distance / distance_m
        gain = np.clip(gain, 0.0, 3.0)
        audio = audio * gain

        # Filtrar frecuencias altas si el objeto está a más de 2 metros
        if distance_m > 2.0:
            cutoff = max(8000.0 - (distance_m - 2.0) * 500.0, 2000.0)
            cutoff_norm = np.clip(cutoff / (self.sample_rate / 2.0), 0.01, 0.99)
            b, a = signal.butter(2, cutoff_norm, btype="low")
            audio = signal.lfilter(b, a, audio)

        return audio

    def apply_room_reverb(self, audio: np.ndarray, distance_m: float,
                          room_size: float = ROOM_REVERB_SIZE) -> np.ndarray:
        """
        Agrega ecos tempranos simples para simular el rebote en la sala.
        """
        reverb_amount = min(distance_m / room_size, 0.8)
        delays_ms = [30, 37, 41, 43]
        gains = [0.5, 0.4, 0.35, 0.3]

        wet = np.zeros_like(audio)
        for delay_ms, gain in zip(delays_ms, gains):
            delay_samples = int(delay_ms * self.sample_rate / 1000)
            if delay_samples < len(audio):
                delayed = np.zeros_like(audio)
                delayed[delay_samples:] = audio[:-delay_samples]
                wet += delayed * gain * reverb_amount

        return audio + wet * 0.3

    def spatialize(self, mono_audio: np.ndarray,
                   azimuth_deg: float,
                   elevation_deg: float = 0.0,
                   distance_m: float = 1.0) -> np.ndarray:
        """
        Transforma un audio mono en un canal estéreo espacializado en 3D.
        """
        if len(mono_audio) == 0:
            return np.zeros((0, 2), dtype=np.float32)

        audio = mono_audio.astype(np.float64).copy()

        # Aplicar atenuación por distancia y ambiente de sala
        audio = self.apply_distance_model(audio, distance_m)
        audio = self.apply_room_reverb(audio, distance_m)

        # Aplicar respuesta al impulso del pabellón auricular
        h_left = self.design_pinna_filter(elevation_deg, "left")
        h_right = self.design_pinna_filter(elevation_deg, "right")
        left = signal.fftconvolve(audio, h_left, mode="same")
        right = signal.fftconvolve(audio, h_right, mode="same")

        # Ajustar volúmenes por diferencia interaural de nivel (ILD)
        ild_db = self.compute_ild(azimuth_deg)
        ild_linear = 10.0 ** (ild_db / 20.0)

        if azimuth_deg >= 0:
            right_gain = min(1.0 + (ild_linear - 1.0) * 0.5, 1.5)
            left_gain = 1.0 / max(ild_linear, 1.0)
        else:
            left_gain = min(1.0 + (1.0 / ild_linear - 1.0) * 0.5, 1.5)
            right_gain = min(ild_linear, 1.0)

        left *= left_gain
        right *= right_gain

        # Desfasar los canales en tiempo (ITD)
        itd_seconds = self.compute_itd(azimuth_deg)
        itd_samples = int(abs(itd_seconds) * self.sample_rate)

        if itd_samples > 0:
            padding = np.zeros(itd_samples)
            if itd_seconds > 0:  # Llega primero al oído derecho
                right = np.concatenate([padding, right])[: len(left)]
            else:                # Llega primero al oído izquierdo
                left = np.concatenate([padding, left])[: len(right)]

        # Prevenir saturación de la onda
        max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-10)
        if max_val > 0.95:
            left /= (max_val / 0.95)
            right /= (max_val / 0.95)

        return np.stack([left, right], axis=-1).astype(np.float32)

"""
Proyecto: Ecos en la Estación - Bucle Principal (Game Loop)
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Motor de lógica del juego. La UI gráfica (GameUI) crea una instancia de
GameEngine, llama a sus métodos de acción (do_forward, do_interact, etc.)
y recibe mensajes de texto para mostrar en pantalla.
Este módulo no imprime nada en terminal — la UI es la responsable de mostrar.
"""

import threading
import time
import numpy as np
from typing import Optional, Tuple

from config import (
    SAMPLE_RATE,
    MOVE_STEP,
    TURN_STEP,
)
from audio.hrtf_engine import HRTFEngine
from audio.mixer import get_mixer, _SD_AVAILABLE
from .player import Player
from .level_1 import Level1
from .narrator import Narrator
from .sound_object import SoundObject


class GameEngine:
    """
    Motor de juego que gestiona el estado del jugador, audio e interacciones.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE, enable_audio: bool = True):
        self.sample_rate = sample_rate
        self.enable_audio = enable_audio
        self.hrtf = HRTFEngine(sample_rate=self.sample_rate)
        self.player = Player()
        self.level = Level1()
        self.narrator = Narrator(sample_rate=self.sample_rate, enable_audio=self.enable_audio)
        self._mixer = get_mixer(sample_rate=self.sample_rate)
        self.running = False

        # Hilo para reproducir sonidos de fondo
        self._ambient_thread: Optional[threading.Thread] = None
        self._ambient_stop = threading.Event()

        # Configuración de tiempos para sonidos repetitivos de cada objeto
        self._ambient_schedule = {
            "Teléfono": {
                "last": 0.0,
                "phase": 0,
                "phase_times": [0.1, 0.35, 0.1, 1.8],
            },
            "Radio": {
                "last": 0.5,
                "interval": 1.6,
            },
            "Puerta de Salida": {
                "last": 1.0,
                "interval": 2.5,
            },
        }

    # ── Sonido ambiental ──────────────────────────────────────────────────────

    def _play_spatialized(self, sound_data: np.ndarray, obj_name: str):
        """Calcula la HRTF y reproduce el audio según posición relativa del objeto."""
        if not _SD_AVAILABLE:
            return
        obj = next((o for o in self.level.objects if o.name == obj_name), None)
        if obj is None or not obj.is_active:
            return
        azimuth, distance = obj.get_relative_spatial_params(self.player)

        raw = sound_data.astype(np.float32)
        max_raw = np.max(np.abs(raw))
        if max_raw < 1e-6:
            return
        raw = raw / max_raw * 0.7

        stereo = self.hrtf.spatialize(raw, azimuth_deg=azimuth, distance_m=distance)
        stereo = stereo * 1.8
        np.clip(stereo, -1.0, 1.0, out=stereo)

        self._mixer.play_ambient(stereo)

    def _ambient_loop(self):
        """Ciclo en segundo plano que emite los sonidos periódicos de los objetos."""
        GLOBAL_COOLDOWN = 1.5

        sched = self._ambient_schedule
        tel = sched["Teléfono"]
        radio = sched["Radio"]
        puerta = sched["Puerta de Salida"]
        now0 = time.monotonic()
        tel["last"] = now0
        radio["last"] = now0 + 2.0
        puerta["last"] = now0 + 4.0

        last_any = now0

        while not self._ambient_stop.is_set():
            now = time.monotonic()

            if now - last_any < GLOBAL_COOLDOWN:
                self._ambient_stop.wait(timeout=0.05)
                continue

            played = False

            # Teléfono: patrón ring-ring
            tel_obj = next((o for o in self.level.objects if o.name == "Teléfono"), None)
            if not played and tel_obj and tel_obj.is_active and not tel_obj.is_interacted:
                phase = tel["phase"]
                if now - tel["last"] >= tel["phase_times"][phase]:
                    tel["last"] = now
                    if phase in (0, 2):
                        self._play_spatialized(self.level.sfx["telefono"], "Teléfono")
                        last_any = now
                        played = True
                    tel["phase"] = (phase + 1) % 4

            # Radio: sonido periódico
            radio_obj = next((o for o in self.level.objects if o.name == "Radio"), None)
            if not played and radio_obj and radio_obj.is_active and not radio_obj.is_interacted:
                if now - radio["last"] >= radio["interval"]:
                    radio["last"] = now
                    self._play_spatialized(self.level.sfx["radio"], "Radio")
                    last_any = now
                    played = True

            # Puerta: zumba solo cuando el jugador tiene las dos pistas
            puerta_activa = (
                self.level.phone_discovered and
                self.level.radio_discovered and
                not self.level.completed
            )
            if not played and puerta_activa:
                if now - puerta["last"] >= puerta["interval"]:
                    puerta["last"] = now
                    self._play_spatialized(self.level.sfx["puerta_hum"], "Puerta de Salida")
                    last_any = now

            self._ambient_stop.wait(timeout=0.05)

    def start_ambient(self):
        """Inicia el hilo de audio ambiental."""
        if not _SD_AVAILABLE:
            return
        self._ambient_stop.clear()
        self._ambient_thread = threading.Thread(
            target=self._ambient_loop, daemon=True, name="AmbientSound"
        )
        self._ambient_thread.start()

    def stop_ambient(self):
        """Detiene el hilo de audio ambiental."""
        self._ambient_stop.set()
        if self._ambient_thread:
            self._ambient_thread.join(timeout=1.0)

    # ── Métodos de acción (llamados por la UI) ────────────────────────────────

    def do_forward(self) -> str:
        """Avanza un paso. Retorna mensaje si choca con pared."""
        moved = self.player.move_forward(MOVE_STEP)
        if moved:
            self.narrator.play_sound(self.level.sfx["pasos"])
            return ""
        else:
            self.narrator.play_sound(self.level.sfx["golpe_pared"])
            return "Colisión con límite perimetral de la sala."
    def do_backward(self) -> str:
        """Retrocede un paso. Retorna mensaje si choca con pared."""
        moved = self.player.move_backward(MOVE_STEP)
        if moved:
            self.narrator.play_sound(self.level.sfx["pasos"])
            return ""
        else:
            self.narrator.play_sound(self.level.sfx["golpe_pared"])
            return "Colisión con límite perimetral de la sala."

        """Gira a la izquierda 90°."""
        self.player.turn_left(TURN_STEP)
        return ""

    def do_turn_right(self) -> str:
        """Gira a la derecha 90°."""
        self.player.turn_right(TURN_STEP)
        return ""

    def do_interact(self) -> str:
        """
        Intenta interactuar con el objeto más cercano.
        Retorna el mensaje de resultado para mostrarlo en la UI.
        """
        best_candidate: Optional[SoundObject] = None
        closest_distance = float("inf")

        for obj in self.level.objects:
            _, dist = obj.get_relative_spatial_params(self.player)
            if dist < closest_distance:
                closest_distance = dist
                best_candidate = obj

        if best_candidate is None:
            self.narrator.play_sound(self.level.sfx["error"])
            return "Ningún objeto detectado en el radio de alcance."

        can_interact, reason = best_candidate.can_interact(self.player)
        if can_interact:
            self.narrator.play_sound(self.level.sfx["confirmacion"], wait=True)
            msg = best_candidate.interact()
            if self.level.completed:
                self.narrator.play_sound(self.level.sfx["puerta"], wait=True)
            return msg
        else:
            azimuth_rel, distance = best_candidate.get_relative_spatial_params(self.player)

            if distance > best_candidate.interaction_radius:
                self.narrator.play_sound(self.level.sfx["error"])
                return f"{best_candidate.name} a {distance:.1f} m. Distancia fuera de rango."

            elif abs(azimuth_rel) > best_candidate.angle_threshold:
                self.narrator.play_sound(self.level.sfx["orientacion_mal"])
                    return f"{best_candidate.name} situado a la derecha ({azimuth_rel:+.0f}°). Orientación frontal requerida."
                else:
                    return f"{best_candidate.name} situado a la izquierda ({azimuth_rel:+.0f}°). Orientación frontal requerida."

            elif best_candidate.name == "Puerta de Salida":
                return reason

                self.narrator.play_sound(self.level.sfx["error"])
                return reason

    def do_listen(self):
        """Reproduce el paisaje sonoro actual desde la posición del jugador."""
        active_objects = self.level.get_active_sound_objects()
        if not active_objects:
            return

        target_length = int(self.sample_rate * 0.8)
        mixed_stereo = np.zeros((target_length, 2), dtype=np.float64)

        for obj in active_objects:
            azimuth_rel, distance = obj.get_relative_spatial_params(self.player)
            sound_src = obj.sound_data
            if len(sound_src) == 0:
                continue

            if len(sound_src) >= target_length:
                chunk = sound_src[:target_length]
            else:
                repeats = int(np.ceil(target_length / len(sound_src)))
                chunk = np.tile(sound_src, repeats)[:target_length]

            spat = self.hrtf.spatialize(chunk, azimuth_deg=azimuth_rel,
                                         elevation_deg=0.0, distance_m=distance)
            mixed_stereo += spat.astype(np.float64)

        peak = np.max(np.abs(mixed_stereo))
        if peak > 0.95:
            mixed_stereo = (mixed_stereo / peak) * 0.95

        self.narrator.play_sound(mixed_stereo.astype(np.float32))

    def close(self):
        """Limpia los recursos de audio al cerrar el juego."""
        self.stop_ambient()
        self._mixer.close()


def run():
    """Función de entrada. Lanza la interfaz gráfica del juego."""
    from ui.visualizer import GameUI
    app = GameUI()
    app.run()

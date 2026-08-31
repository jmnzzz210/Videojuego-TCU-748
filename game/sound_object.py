"""
Proyecto: Ecos en la Estación - Objetos Sonoros e Interacción
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Clase SoundObject que representa emisores de audio interactivos en el mapa.
Calcula su ubicación relativa al jugador (azimuth y distancia) y verifica
las condiciones necesarias para poder interactuar.
"""

from typing import Callable, Optional, Tuple
import numpy as np

from config import (
    INTERACTION_DISTANCE,
    INTERACTION_ANGLE_THRESHOLD,
    SAMPLE_RATE,
)
from .player import Player


class SoundObject:
    """
    Representa un objeto interactivo que emite sonido en el entorno 2D.
    """

    def __init__(self,
                 name: str,
                 x: float,
                 y: float,
                 sound_data: np.ndarray,
                 interaction_radius: float = INTERACTION_DISTANCE,
                 angle_threshold: float = INTERACTION_ANGLE_THRESHOLD,
                 description: str = "",
                 interaction_text: str = "",
                 is_active: bool = True,
                 is_interactable: bool = True):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.sound_data = sound_data.astype(np.float32)
        self.interaction_radius = float(interaction_radius)
        self.angle_threshold = float(angle_threshold)
        self.description = description
        self.interaction_text = interaction_text
        self.is_active = is_active
        self.is_interactable = is_interactable
        self.is_interacted = False
        self.on_interact_callback: Optional[Callable[[], str]] = None

    def get_relative_spatial_params(self, player: Player) -> Tuple[float, float]:
        """
        Calcula el ángulo relativo (azimuth) y la distancia desde el jugador al objeto.
        """
        dx = self.x - player.x
        dy = self.y - player.y

        # Calculo de la distancia en metros
        distance = max(float(np.hypot(dx, dy)), 0.1)

        # Calculo del ángulo en el mapa
        angle_world = float(np.degrees(np.arctan2(dx, dy)))

        # Azimuth relativo a la vista actual del jugador
        azimuth_rel = ((angle_world - player.facing_deg + 180.0) % 360.0) - 180.0

        return azimuth_rel, distance

    def can_interact(self, player: Player) -> Tuple[bool, str]:
        """
        Evalúa si el jugador está lo suficientemente cerca y de frente al objeto.
        """
        if not self.is_interactable:
            return False, f"{self.name} no permite interacción."

        azimuth_rel, distance = self.get_relative_spatial_params(player)

        if distance > self.interaction_radius:
            return False, f"Demasiado lejos de {self.name} ({distance:.1f}m > {self.interaction_radius:.1f}m)."

        if abs(azimuth_rel) > self.angle_threshold:
            lado = "a tu derecha" if azimuth_rel > 0 else "a tu izquierda"
            return False, f"{self.name} está cerca pero {lado} ({azimuth_rel:+.0f}°). Gira para encararlo."

        return True, f"En posición para interactuar con {self.name}."

    def interact(self) -> str:
        """
        Realiza la interacción con el objeto y retorna el mensaje correspondiente.
        """
        self.is_interacted = True
        if self.on_interact_callback:
            custom_msg = self.on_interact_callback()
            if custom_msg:
                return custom_msg

        return self.interaction_text or f"Has interactuado con {self.name}."

    def get_clock_direction(self, player: Player) -> str:
        """
        Obtiene la dirección relativa en formato de horas de reloj (ejemplo: 12:00, 03:00).
        """
        azimuth_rel, _ = self.get_relative_spatial_params(player)
        clock_deg = (azimuth_rel + 360.0) % 360.0
        hour = int(round(clock_deg / 30.0)) % 12
        hour = 12 if hour == 0 else hour
        return f"{hour:02d}:00"

    def __repr__(self) -> str:
        return f"SoundObject({self.name}, pos=({self.x:.1f}, {self.y:.1f}), active={self.is_active})"

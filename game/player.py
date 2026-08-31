"""
Proyecto: Ecos en la Estación - Estado y Cinemática del Jugador
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Clase que representa la posición, orientación y movimiento del jugador
en el espacio 2D de la habitación, incluyendo control de colisiones con los límites.
"""

import numpy as np
from typing import Tuple

from config import (
    START_X,
    START_Y,
    START_FACING_DEG,
    MOVE_STEP,
    TURN_STEP,
    ROOM_X_MIN,
    ROOM_X_MAX,
    ROOM_Y_MIN,
    ROOM_Y_MAX,
)


class Player:
    """
    Clase que maneja las coordenadas y la dirección hacia la que mira el jugador.
    """

    def __init__(self, x: float = START_X, y: float = START_Y, facing_deg: float = START_FACING_DEG):
        self.x: float = float(x)
        self.y: float = float(y)
        self.facing_deg: float = self._normalize_angle(facing_deg)

    @staticmethod
    def _normalize_angle(angle_deg: float) -> float:
        """Mantiene los ángulos en el rango de -180 a 180 grados."""
        return ((angle_deg + 180.0) % 360.0) - 180.0

    def move_forward(self, step: float = MOVE_STEP) -> bool:
        """
        Avanza un paso hacia el frente de la dirección actual.
        """
        rad = np.radians(self.facing_deg)
        dx = np.sin(rad) * step
        dy = np.cos(rad) * step
        return self._try_move(self.x + dx, self.y + dy)

    def move_backward(self, step: float = MOVE_STEP) -> bool:
        """
        Retrocede un paso respecto a la dirección actual.
        """
        rad = np.radians(self.facing_deg)
        dx = -np.sin(rad) * step
        dy = -np.cos(rad) * step
        return self._try_move(self.x + dx, self.y + dy)

    def turn_left(self, step_deg: float = TURN_STEP) -> float:
        """
        Gira la vista del jugador hacia la izquierda.
        """
        self.facing_deg = self._normalize_angle(self.facing_deg - step_deg)
        return self.facing_deg

    def turn_right(self, step_deg: float = TURN_STEP) -> float:
        """
        Gira la vista del jugador hacia la derecha.
        """
        self.facing_deg = self._normalize_angle(self.facing_deg + step_deg)
        return self.facing_deg

    def _try_move(self, new_x: float, new_y: float) -> bool:
        """
        Comprueba que la nueva posición no sobrepase las paredes de la habitación.
        """
        margin = 0.1
        if (ROOM_X_MIN + margin <= new_x <= ROOM_X_MAX - margin and
                ROOM_Y_MIN + margin <= new_y <= ROOM_Y_MAX - margin):
            self.x = new_x
            self.y = new_y
            return True
        return False

    @property
    def position(self) -> Tuple[float, float]:
        """Devuelve la posición actual (x, y)."""
        return self.x, self.y

    def get_compass_direction(self) -> str:
        """
        Devuelve el nombre cardinal según los grados a los que mira el jugador.
        """
        deg = self.facing_deg
        if -22.5 <= deg <= 22.5:
            return "Norte (Frente)"
        elif 22.5 < deg <= 67.5:
            return "Noreste (Adelante-Derecha)"
        elif 67.5 < deg <= 112.5:
            return "Este (Derecha)"
        elif 112.5 < deg <= 157.5:
            return "Sureste (Atrás-Derecha)"
        elif deg > 157.5 or deg < -157.5:
            return "Sur (Atrás)"
        elif -157.5 <= deg < -112.5:
            return "Suroeste (Atrás-Izquierda)"
        elif -112.5 <= deg < -67.5:
            return "Oeste (Izquierda)"
        elif -67.5 <= deg < -22.5:
            return "Noroeste (Adelante-Izquierda)"
        return "Desconocido"

    def __repr__(self) -> str:
        return f"Player(x={self.x:.2f}, y={self.y:.2f}, facing={self.facing_deg:.1f}° [{self.get_compass_direction()}])"

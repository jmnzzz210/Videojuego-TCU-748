"""
Proyecto: Ecos en la Estación - Control de Entrada por Teclado
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Captura pulsaciones de teclas en tiempo real desde la consola de terminal (sin requerir presionar Enter).
Configura la terminal en modo cbreak no bloqueante para leer flechas de dirección y teclas WASD.
"""

import sys
import os
import select
from enum import Enum, auto
from typing import Optional


class Action(Enum):
    FORWARD = auto()       # Avanzar (W / Flecha arriba)
    BACKWARD = auto()      # Retroceder (S / Flecha abajo)
    TURN_LEFT = auto()     # Girar izquierda (A / Flecha izquierda)
    TURN_RIGHT = auto()    # Girar derecha (D / Flecha derecha)
    INTERACT = auto()      # Interactuar (Espacio / Enter / E)
    STATUS = auto()        # Ver estado (H / ?)
    LISTEN = auto()        # Escuchar sonido ambiental (L / P)
    QUIT = auto()          # Salir (Q / ESC)
    UNKNOWN = auto()


class KeyboardController:
    """
    Gestor para la lectura de teclas en modo no bloqueante en terminales Unix/Linux.
    """

    def __init__(self):
        self.is_tty = sys.stdin.isatty()
        self._old_settings = None

    def __enter__(self):
        """
        Pone la terminal en modo cbreak al iniciar.
        """
        if self.is_tty and os.name != "nt":
            try:
                import termios
                import tty
                self._old_settings = termios.tcgetattr(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
            except Exception:
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Restaura la configuración original de la terminal al salir.
        """
        if self._old_settings is not None and self.is_tty and os.name != "nt":
            try:
                import termios
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass

    def get_key(self, timeout_sec: Optional[float] = None) -> Optional[str]:
        """
        Lee una tecla presionada en la consola sin bloquear indefinidamente.
        """
        if not self.is_tty:
            try:
                line = sys.stdin.readline()
                return line.strip() if line else None
            except Exception:
                return None

        # Usar select con tiempo máximo de 50ms para permitir fluidez en el hilo de audio
        effective_timeout = 0.05 if timeout_sec is None else min(timeout_sec, 0.05)
        rlist, _, _ = select.select([sys.stdin], [], [], effective_timeout)
        if not rlist:
            return None

        try:
            char1 = sys.stdin.read(1)
            # Procesar secuencias de escape para las flechas del teclado
            if char1 == "\x1b":
                rlist2, _, _ = select.select([sys.stdin], [], [], 0.05)
                if rlist2:
                    char2 = sys.stdin.read(1)
                    if char2 == "[":
                        char3 = sys.stdin.read(1)
                        return f"\x1b[{char3}"
                    return f"\x1b{char2}"
                return "\x1b"
            return char1
        except Exception:
            return None

    def parse_action(self, key_str: Optional[str]) -> Action:
        """
        Mapea el caracter o código recibido a una acción del juego.
        """
        if not key_str:
            return Action.UNKNOWN

        k = key_str.lower()

        if key_str == "\x1b[A" or k in ("w", "k"):
            return Action.FORWARD
        elif key_str == "\x1b[B" or k in ("s", "j"):
            return Action.BACKWARD
        elif key_str == "\x1b[D" or k in ("a",):
            return Action.TURN_LEFT
        elif key_str == "\x1b[C" or k in ("d",):
            return Action.TURN_RIGHT
        elif key_str in (" ", "\r", "\n") or k in ("e", "i"):
            return Action.INTERACT
        elif k in ("h", "?"):
            return Action.STATUS
        elif k in ("l", "p"):
            return Action.LISTEN
        elif key_str == "\x1b" or k in ("q", "x"):
            return Action.QUIT

        return Action.UNKNOWN

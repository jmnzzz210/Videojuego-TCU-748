"""
Proyecto: Ecos en la Estación - Escenario Nivel 1
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Define la lógica del primer nivel del juego: objetos sonoros (teléfono, radio, puerta),
posiciones en el mapa, pistas recolectables y condiciones para completar la misión.
"""

from typing import List, Dict
import numpy as np
from pathlib import Path

from config import ASSETS_DIR, SAMPLE_RATE
from audio.sound_generator import load_wav, generate_default_assets
from .sound_object import SoundObject
from .player import Player


class Level1:
    """
    Controlador de la escena y objetivos del Nivel 1.
    """

    def __init__(self, assets_dir: Path = ASSETS_DIR):
        self.assets_dir = assets_dir
        
        # Generar archivos de audio si no existen
        generate_default_assets(self.assets_dir)

        # Cargar los sonidos necesarios para este nivel
        self.sfx: Dict[str, np.ndarray] = {
            "telefono":         load_wav(self.assets_dir / "telefono.wav"),
            "radio":            load_wav(self.assets_dir / "radio.wav"),
            "puerta":           load_wav(self.assets_dir / "puerta_abrir.wav"),
            "pasos":            load_wav(self.assets_dir / "pasos.wav"),
            "confirmacion":     load_wav(self.assets_dir / "confirmacion.wav"),
            "error":            load_wav(self.assets_dir / "error.wav"),
            "golpe_pared":      load_wav(self.assets_dir / "golpe_pared.wav"),
            "puerta_bloqueada": load_wav(self.assets_dir / "puerta_bloqueada.wav"),
            "orientacion_mal":  load_wav(self.assets_dir / "orientacion_mal.wav"),
            "puerta_hum":       load_wav(self.assets_dir / "puerta_hum.wav"),
        }

        # Banderas de avance en el nivel
        self.phone_discovered: bool = False
        self.radio_discovered: bool = False
        self.door_unlocked: bool = False
        self.completed: bool = False

        self.objects: List[SoundObject] = []
        self._build_scene()

    def _build_scene(self):
        """
        Crea los objetos interactivos y los ubica en sus coordenadas.
        """
        # Teléfono ubicado a la izquierda (-3, 0)
        telefono = SoundObject(
            name="Teléfono",
            x=-3.0,
            y=0.0,
            sound_data=self.sfx["telefono"],
            description="Un teléfono de escritorio que suena periódicamente.",
            interaction_text="Contestador: 'La primera parte del código de salida es: 7...'"
        )

        def interact_telefono() -> str:
            self.phone_discovered = True
            return "Contestador: 'La primera parte del código de salida es: 7. Sintoniza la radio para el resto...'"

        telefono.on_interact_callback = interact_telefono

        # Radio ubicada a la derecha (3, 0)
        radio = SoundObject(
            name="Radio",
            x=3.0,
            y=0.0,
            sound_data=self.sfx["radio"],
            description="Una pequeña radio transmitiendo datos entre estática.",
            interaction_text="Transmisión: '...el código concluye con: 4 8...'"
        )

        def interact_radio() -> str:
            self.radio_discovered = True
            return "Transmisión: '...el código concluye con: 4 8. Código total de salida: 7-4-8.'"

        radio.on_interact_callback = interact_radio

        # Puerta ubicada al frente (0, 4)
        puerta = SoundObject(
            name="Puerta de Salida",
            x=0.0,
            y=4.0,
            sound_data=self.sfx["puerta"],
            description="Una puerta metálica pesada con cerradura electrónica.",
            interaction_text="La puerta está bloqueada."
        )

        def interact_puerta() -> str:
            if self.phone_discovered and self.radio_discovered:
                self.door_unlocked = True
                self.completed = True
                return "Has introducido el código 7-4-8. El cerrojo se abre y la puerta se destraba. ¡Felicidades! Completaste el tutorial, pronto habrá continuación de la historia."
            else:
                pistas_faltantes = []
                if not self.phone_discovered:
                    pistas_faltantes.append("el teléfono a la izquierda")
                if not self.radio_discovered:
                    pistas_faltantes.append("la radio a la derecha")
                return f"La puerta requiere un código numérico. Te falta inspeccionar: {' y '.join(pistas_faltantes)}."

        puerta.on_interact_callback = interact_puerta

        self.objects = [telefono, radio, puerta]

    def get_active_sound_objects(self) -> List[SoundObject]:
        """
        Retorna la lista de objetos sonoros activos.
        """
        return [obj for obj in self.objects if obj.is_active]

    def get_status_summary(self, player: Player) -> List[str]:
        """
        Genera el resumen de posición de los objetos respecto al jugador.
        """
        summary = []
        for obj in self.objects:
            azimuth, dist = obj.get_relative_spatial_params(player)
            clock = obj.get_clock_direction(player)
            
            if azimuth > 20:
                pos_txt = f"{azimuth:+.0f}° (Derecha)"
            elif azimuth < -20:
                pos_txt = f"{azimuth:+.0f}° (Izquierda)"
            else:
                pos_txt = f"{azimuth:+.0f}° (Al Frente)"

            status_icon = "[OK]" if obj.is_interacted else "[  ]"
            summary.append(
                f"{status_icon} {obj.name}: a {dist:.1f}m en dirección {clock} [{pos_txt}]"
            )
        return summary

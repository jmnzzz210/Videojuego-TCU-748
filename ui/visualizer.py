"""
Proyecto: Ecos en la Estación - Interfaz Gráfica Completa
Autores: Marvin Coto Jiménez y Brandon Jiménez Campos

Descripción:
Aplicación gráfica con Tkinter de alta legibilidad y tipografía grande.
Incluye tres pantallas:
  1. Bienvenida: título grande, objetivo del tutorial, controles y botón JUGAR.
  2. Juego: pantalla en negro para inmersión auditiva total (audio 3D HRTF) con
     subtítulos de interacción en texto de gran tamaño.
  3. Final: mensaje de tutorial completado y créditos.
"""

import math
from typing import Optional

try:
    import tkinter as tk
    _TK_AVAILABLE = True
except ImportError:
    _TK_AVAILABLE = False


# =============================================================================
# MODO DE DEPURACIÓN VISUAL
# Si se cambia a True, se vuelve a mostrar el mapa 2D, el radar y las distancias
# en metros que están comentadas abajo para realizar pruebas.
# =============================================================================
DEBUG_VISUAL_MODE = False


# ── Paleta de Colores ────────────────────────────────────────────────────────
BG_BLACK     = "#000000"   # Negro absoluto para inmersión
BG_DARK      = "#0f141c"   # Fondo de menús
BG_PANEL     = "#18202c"   # Tarjetas y paneles
BG_CARD      = "#242f3d"   # Botones y cajas secundarias
ACCENT       = "#e63946"   # Rojo de acento
ACCENT_HOVER = "#c92a37"
GREEN        = "#2a9d8f"   # Verde de éxito
GREEN_BRIGHT = "#48cae4"
YELLOW       = "#f4a261"   # Amarillo/dorado
WHITE        = "#ffffff"   # Texto principal
GRAY_LIGHT   = "#e0e6ed"   # Texto secundario claro
GRAY         = "#94a3b8"   # Texto terciario
WALL_CLR     = "#334155"

# ── Dimensiones de la Sala (Metros) ──────────────────────────────────────────
ROOM_X_MIN, ROOM_X_MAX = -4.0, 4.0
ROOM_Y_MIN, ROOM_Y_MAX = -2.0, 5.0


class GameUI:
    """
    Gestor de la interfaz gráfica del videojuego con tres pantallas principales
    y tipografía de gran tamaño.
    """

    def __init__(self):
        if not _TK_AVAILABLE:
            raise RuntimeError("Tkinter no está instalado en este sistema.")

        self.root = tk.Tk()
        self.root.title("Ecos en la Estación")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        # Dimensiones de la ventana
        self.WIN_W = 1040
        self.WIN_H = 750
        self._center_window(self.WIN_W, self.WIN_H)

        self.engine = None
        self._message = ""
        self._update_job = None

        # Mostrar pantalla inicial de bienvenida
        self._show_welcome()

    def _center_window(self, w: int, h: int):
        """Centra la ventana en el monitor del usuario."""
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _clear(self):
        """Limpia los widgets y cancela temporizadores activos."""
        if self._update_job is not None:
            self.root.after_cancel(self._update_job)
            self._update_job = None
        self.root.unbind("<Key>")
        for widget in self.root.winfo_children():
            widget.destroy()

    # =========================================================================
    # PANTALLA 1: BIENVENIDA (Tipografía Mucho Más Grande)
    # =========================================================================

    def _show_welcome(self):
        """Construye la pantalla de inicio con instrucciones y tipografía de gran tamaño."""
        self._clear()
        self.root.configure(bg=BG_DARK)
        self._center_window(self.WIN_W, self.WIN_H)

        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(expand=True, fill="both")

        # Barra decorativa superior
        tk.Frame(outer, bg=ACCENT, height=5).pack(fill="x")

        center = tk.Frame(outer, bg=BG_DARK)
        center.pack(expand=True, fill="both", pady=20, padx=50)

        # Título principal grande
        tk.Label(
            center,
            text="ECOS EN LA ESTACIÓN",
            font=("Helvetica", 42, "bold"),
            bg=BG_DARK, fg=WHITE
        ).pack(pady=(5, 20))

        # Cuadro de objetivo y contexto con texto grande
        desc_box = tk.Frame(center, bg=BG_PANEL, padx=32, pady=18, highlightthickness=1, highlightbackground=WALL_CLR)
        desc_box.pack(fill="x", pady=(0, 18))

        tk.Label(
            desc_box,
            text="OBJETIVO DE LA MISIÓN",
            font=("Helvetica", 19, "bold"),
            bg=BG_PANEL, fg=ACCENT
        ).pack(anchor="w", pady=(0, 10))

        texto_objetivo = (
            "• Estás en una habitación completamente a oscuras.\n"
            "• Utiliza únicamente tus oídos y auriculares para ubicar los sonidos.\n"
            "• Escucha el teléfono y la radio para encontrar las pistas del código.\n"
            "• Dirígete a la puerta e introduce el código para escapar."
        )
        tk.Label(
            desc_box,
            text=texto_objetivo,
            font=("Helvetica", 16),
            bg=BG_PANEL, fg=GRAY_LIGHT,
            justify="left", anchor="w",
            pady=4
        ).pack(anchor="w")

        # Cuadro de controles con teclas grandes
        ctrl_box = tk.Frame(center, bg=BG_PANEL, padx=32, pady=18, highlightthickness=1, highlightbackground=WALL_CLR)
        ctrl_box.pack(fill="x", pady=(0, 22))

        tk.Label(
            ctrl_box,
            text="CONTROLES DEL JUEGO",
            font=("Helvetica", 19, "bold"),
            bg=BG_PANEL, fg=ACCENT
        ).pack(anchor="w", pady=(0, 12))

        grid_frame = tk.Frame(ctrl_box, bg=BG_PANEL)
        grid_frame.pack(fill="x")

        controles = [
            ("W  /  ↑", "Avanzar un paso"),
            ("S  /  ↓", "Retroceder un paso"),
            ("A  /  ←", "Girar a la izquierda (90°)"),
            ("D  /  →", "Girar a la derecha (90°)"),
            ("ESPACIO / E", "Interactuar con objeto al frente"),
            ("L  /  P", "Escuchar pulso sonoro 3D"),
        ]

        for i, (tecla, accion) in enumerate(controles):
            row = i // 2
            col = i % 2
            celda = tk.Frame(grid_frame, bg=BG_PANEL)
            celda.grid(row=row, column=col, sticky="w", padx=16, pady=5)

            tk.Label(
                celda, text=tecla,
                font=("Helvetica", 16, "bold"),
                bg=BG_CARD, fg=WHITE,
                padx=12, pady=4
            ).pack(side="left")

            tk.Label(
                celda, text=f"  {accion}",
                font=("Helvetica", 16),
                bg=BG_PANEL, fg=GRAY_LIGHT
            ).pack(side="left")

        # Botón de Inicio prominente
        btn_jugar = tk.Button(
            center,
            text="  ▶  JUGAR  ",
            font=("Helvetica", 24, "bold"),
            bg=ACCENT, fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            padx=55, pady=14,
            cursor="hand2",
            command=self._start_game
        )
        btn_jugar.pack(pady=(8, 10))

        tk.Label(
            center,
            text="🎧 Recuerda colocarte auriculares para percibir la dirección de los sonidos",
            font=("Helvetica", 15),
            bg=BG_DARK, fg=GRAY
        ).pack()

        # Pie de página con créditos
        footer = tk.Frame(outer, bg=BG_PANEL, pady=10)
        footer.pack(fill="x", side="bottom")
        tk.Label(
            footer,
            text="Autores: Marvin Coto Jiménez y Brandon Jiménez Campos  ·  TCU-748 UCR",
            font=("Helvetica", 13),
            bg=BG_PANEL, fg=GRAY
        ).pack()

    # =========================================================================
    # PANTALLA 2: JUEGO (Pantalla en Negro / Audio Inmersivo)
    # =========================================================================

    def _start_game(self):
        """Inicializa el motor acústico y pasa a la pantalla del juego."""
        from game.game_loop import GameEngine
        self.engine = GameEngine()
        self.engine.running = True
        self.engine.start_ambient()
        self._message = "La habitación está a oscuras. Escucha a tu alrededor para orientarte..."
        self._show_game_screen()

    def _show_game_screen(self):
        """
        Construye la pantalla de juego.
        Por defecto, la pantalla es completamente negra para inmersión auditiva.
        Muestra subtítulos grandes en la parte inferior para lectura accesible.
        """
        self._clear()
        self.root.configure(bg=BG_BLACK)
        self._center_window(self.WIN_W, self.WIN_H)

        # ── Barra superior minimalista ───────────────────────────────────────
        topbar = tk.Frame(self.root, bg=BG_BLACK, pady=10, padx=20)
        topbar.pack(fill="x")

        tk.Label(
            topbar,
            text="ECOS EN LA ESTACIÓN",
            font=("Helvetica", 16, "bold"),
            bg=BG_BLACK, fg="#444444"
        ).pack(side="left")

        # Botón para regresar al menú si es necesario
        tk.Button(
            topbar,
            text="Volver al Menú",
            font=("Helvetica", 14, "bold"),
            bg="#1a1a1a", fg=GRAY_LIGHT,
            activebackground="#333333", activeforeground=WHITE,
            relief="flat", padx=16, pady=6, cursor="hand2",
            command=self._confirm_exit_to_menu
        ).pack(side="right")

        # ── Área Central de Juego ────────────────────────────────────────────
        # Si DEBUG_VISUAL_MODE está en False: Pantalla completamente en negro.
        # Si DEBUG_VISUAL_MODE está en True: Se muestra el mapa y radares.
        self.game_container = tk.Frame(self.root, bg=BG_BLACK)
        self.game_container.pack(expand=True, fill="both")

        if DEBUG_VISUAL_MODE:
            # =================================================================
            # CÓDIGO DE DEPURACIÓN VISUAL (MAPA 2D Y DISTANCIAS LATERALES)
            # Para reactivar, cambiar la variable DEBUG_VISUAL_MODE = True arriba.
            # =================================================================
            self._build_debug_visual_widgets(self.game_container)
        else:
            # Modo Inmersión Auditiva: Pantalla completamente en negro
            self.center_info = tk.Frame(self.game_container, bg=BG_BLACK)
            self.center_info.pack(expand=True)

            tk.Label(
                self.center_info,
                text="🎧",
                font=("Helvetica", 64),
                bg=BG_BLACK, fg="#222222"
            ).pack(pady=(0, 14))

            tk.Label(
                self.center_info,
                text="Usa las teclas W, A, S, D para moverte y ESPACIO para interactuar",
                font=("Helvetica", 18),
                bg=BG_BLACK, fg="#333333"
            ).pack()

        # ── Barra inferior: Subtítulos de Interacción en Texto Grande ────────
        self.msg_container = tk.Frame(
            self.root, bg="#0a0a0a", pady=22, padx=30,
            highlightthickness=1, highlightbackground="#1f1f1f"
        )
        self.msg_container.pack(fill="x", side="bottom")

        self.lbl_msg = tk.Label(
            self.msg_container,
            text=self._message,
            font=("Helvetica", 20, "bold"),
            bg="#0a0a0a", fg=WHITE,
            anchor="center", wraplength=980, justify="center"
        )
        self.lbl_msg.pack(fill="x")

        # Captura de teclado directamente en la ventana
        self.root.bind("<Key>", self._on_key)
        self.root.focus_set()

        # Actualización periódica en caso de depuración visual
        if DEBUG_VISUAL_MODE:
            self._update_display()

    def _on_key(self, event):
        """Procesa las teclas presionadas en la ventana del juego."""
        if self.engine is None or not self.engine.running:
            return

        key = event.keysym.lower()
        msg = ""

        # Controles de movimiento
        if key in ("w", "up"):
            msg = self.engine.do_forward()

        elif key in ("s", "down"):
            msg = self.engine.do_backward()

        elif key in ("a", "left"):
            self.engine.do_turn_left()

        elif key in ("d", "right"):
            self.engine.do_turn_right()

        # Interacción
        elif key in ("e", "space", "return"):
            msg = self.engine.do_interact()

        # Escucha acústica
        elif key in ("l", "p"):
            self.engine.do_listen()
            msg = "Escuchando el entorno en 360 grados..."

        # Mostrar mensaje resultante en tipografía grande
        if msg:
            self._message = msg
            self.lbl_msg.config(text=msg)

        # Si el nivel se completó, pasar a la pantalla final
        if self.engine.level.completed:
            self.root.after(1600, self._show_completion)
        elif DEBUG_VISUAL_MODE:
            self._update_display()

    # =========================================================================
    # SECCIÓN COMENTADA / DEPURACIÓN: WIDGETS VISUALES (MAPA Y DISTANCIAS)
    # =========================================================================
    def _build_debug_visual_widgets(self, parent):
        """
        Construye el mapa 2D y paneles laterales cuando DEBUG_VISUAL_MODE = True.
        (Por defecto deshabilitado según lo solicitado).
        """
        map_frame = tk.Frame(parent, bg=BG_PANEL, padx=12, pady=12)
        map_frame.pack(side="left", padx=20, pady=20)

        self.MAP_W = 440
        self.MAP_H = 420
        self.canvas = tk.Canvas(
            map_frame,
            width=self.MAP_W, height=self.MAP_H,
            bg=BG_DARK, highlightthickness=1,
            highlightbackground=WALL_CLR
        )
        self.canvas.pack()

        # Panel lateral con coordenadas y distancias en metros
        side_frame = tk.Frame(parent, bg=BG_PANEL, padx=20, pady=20)
        side_frame.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        tk.Label(side_frame, text="DATOS DE PRUEBA (DEBUG)", font=("Helvetica", 16, "bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(anchor="w", pady=(0, 10))

        self.lbl_debug_pos = tk.Label(side_frame, text="Posición: -", font=("Helvetica", 15),
                                      bg=BG_PANEL, fg=WHITE, anchor="w")
        self.lbl_debug_pos.pack(fill="x", pady=4)

        self.lbl_debug_dir = tk.Label(side_frame, text="Mirando: -", font=("Helvetica", 15),
                                      bg=BG_PANEL, fg=WHITE, anchor="w")
        self.lbl_debug_dir.pack(fill="x", pady=4)

        self.lbl_debug_dist = tk.Label(side_frame, text="Distancias:\n• Teléfono: -\n• Radio: -\n• Puerta: -",
                                       font=("Helvetica", 15), bg=BG_PANEL, fg=GRAY_LIGHT,
                                       justify="left", anchor="w")
        self.lbl_debug_dist.pack(fill="x", pady=10)

    def _world_to_canvas(self, wx: float, wy: float):
        """Convierte coordenadas del juego (metros) a píxeles de canvas para el mapa debug."""
        margin = 25
        cw = self.MAP_W - 2 * margin
        ch = self.MAP_H - 2 * margin
        px = margin + (wx - ROOM_X_MIN) / (ROOM_X_MAX - ROOM_X_MIN) * cw
        py = margin + (ROOM_Y_MAX - wy) / (ROOM_Y_MAX - ROOM_Y_MIN) * ch
        return px, py

    def _update_display(self):
        """Actualiza el mapa y textos de depuración si DEBUG_VISUAL_MODE está activo."""
        if not DEBUG_VISUAL_MODE or self.engine is None:
            return

        c = self.canvas
        c.delete("all")

        # Dibujar límites del cuarto
        x0, y0 = self._world_to_canvas(ROOM_X_MIN, ROOM_Y_MIN)
        x1, y1 = self._world_to_canvas(ROOM_X_MAX, ROOM_Y_MAX)
        c.create_rectangle(x0, y0, x1, y1, outline=WALL_CLR, width=2)

        player = self.engine.player
        level = self.engine.level
        ppx, ppy = self._world_to_canvas(player.x, player.y)

        # Dibujar objetos
        for obj in level.objects:
            ox, oy = self._world_to_canvas(obj.x, obj.y)
            c.create_oval(ox - 12, oy - 12, ox + 12, oy + 12, fill=YELLOW, outline=WHITE)
            c.create_text(ox, oy, text=obj.name[:3].upper(), font=("Helvetica", 9, "bold"))

        # Dibujar jugador y flecha de dirección
        c.create_oval(ppx - 10, ppy - 10, ppx + 10, ppy + 10, fill=ACCENT, outline=WHITE)
        rad = math.radians(player.facing_deg - 90)
        ax = ppx + 22 * math.cos(rad)
        ay = ppy + 22 * math.sin(rad)
        c.create_line(ppx, ppy, ax, ay, fill="#ff8fa3", width=3, arrow="last")

        # Actualizar datos de texto
        self.lbl_debug_pos.config(text=f"Posición: ({player.x:+.1f} m, {player.y:+.1f} m)")
        self.lbl_debug_dir.config(text=f"Mirando: {player.get_compass_direction()}")

        dist_texts = []
        for obj in level.objects:
            _, dist = obj.get_relative_spatial_params(player)
            dist_texts.append(f"• {obj.name}: a {dist:.1f} m")
        self.lbl_debug_dist.config(text="Distancias:\n" + "\n".join(dist_texts))

        self._update_job = self.root.after(100, self._update_display)

    def _confirm_exit_to_menu(self):
        """Detiene el audio y regresa a la pantalla de bienvenida."""
        if self.engine:
            self.engine.stop_ambient()
            self.engine._mixer.close()
            self.engine = None
        self._show_welcome()

    # =========================================================================
    # PANTALLA 3: COMPLETADO / VICTORIA (Tipografía Mucho Más Grande)
    # =========================================================================

    def _show_completion(self):
        """Pantalla de felicitaciones con letra grande."""
        if self.engine:
            self.engine.stop_ambient()
            self.engine._mixer.close()
            self.engine = None

        self._clear()
        self.root.configure(bg=BG_DARK)
        self._center_window(self.WIN_W, self.WIN_H)

        tk.Frame(self.root, bg=GREEN, height=6).pack(fill="x")

        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(expand=True, fill="both", pady=40, padx=60)

        # Mensaje de Felicitaciones
        tk.Label(
            outer,
            text="¡FELICIDADES!",
            font=("Helvetica", 46, "bold"),
            bg=BG_DARK, fg=GREEN_BRIGHT
        ).pack(pady=(0, 16))

        tk.Label(
            outer,
            text="Completaste el tutorial.",
            font=("Helvetica", 28, "bold"),
            bg=BG_DARK, fg=WHITE
        ).pack(pady=(0, 12))

        tk.Label(
            outer,
            text="Pronto habrá continuación de la historia.",
            font=("Helvetica", 22),
            bg=BG_DARK, fg=GRAY_LIGHT
        ).pack(pady=(0, 30))

        tk.Frame(outer, bg=WALL_CLR, height=1).pack(fill="x", pady=(0, 25))

        # Créditos
        tk.Label(
            outer,
            text="Desarrollado por:",
            font=("Helvetica", 16),
            bg=BG_DARK, fg=GRAY
        ).pack(pady=(0, 6))

        tk.Label(
            outer,
            text="Marvin Coto Jiménez  ·  Brandon Jiménez Campos",
            font=("Helvetica", 22, "bold"),
            bg=BG_DARK, fg=WHITE
        ).pack(pady=(0, 8))

        tk.Label(
            outer,
            text="Proyecto TCU-748  ·  Universidad de Costa Rica",
            font=("Helvetica", 16),
            bg=BG_DARK, fg=YELLOW
        ).pack(pady=(0, 35))

        # Botones de navegación grandes
        btn_box = tk.Frame(outer, bg=BG_DARK)
        btn_box.pack()

        tk.Button(
            btn_box,
            text="  Volver al Menú Principal  ",
            font=("Helvetica", 18, "bold"),
            bg=BG_PANEL, fg=WHITE,
            activebackground=BG_CARD, activeforeground=WHITE,
            relief="flat", padx=30, pady=12, cursor="hand2",
            command=self._show_welcome
        ).pack(side="left", padx=16)

        tk.Button(
            btn_box,
            text="  Salir del Juego  ",
            font=("Helvetica", 18, "bold"),
            bg=ACCENT, fg=WHITE,
            activebackground=ACCENT_HOVER, activeforeground=WHITE,
            relief="flat", padx=30, pady=12, cursor="hand2",
            command=self.root.destroy
        ).pack(side="left", padx=16)

    def run(self):
        """Inicia el bucle principal de la aplicación gráfica."""
        self.root.mainloop()
        if self.engine:
            self.engine.close()

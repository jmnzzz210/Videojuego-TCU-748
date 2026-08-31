# Ecos en la Estación 🎧
### Videojuego Accesible basado en Audio Espacial 3D (HRTF)

**TCU-748: Tecnoinclusión**  
**Universidad de Costa Rica (UCR)**  
**Autores:** Marvin Coto Jiménez y Brandon Jiménez Campos  

---

## 📖 Descripción del Proyecto

**Ecos en la Estación** es un prototipo de videojuego de exploración accesible basado en **Audio Espacial 3D** mediante técnicas de **HRTF** (*Head-Related Transfer Function*), diseñado para personas no videntes y experiencias inmersivas puramente auditivas.

Al presionar **JUGAR**, la aplicación pasa a una pantalla oscura para promover la inmersión auditiva completa. El jugador debe orientarse en el espacio de la habitación utilizando sus oídos para identificar fuentes de sonido (teléfono, radio y puerta de salida), descifrar las pistas acústicas y escapar.

---

## 🎧 Requisitos Previos

1. **Python 3.8 o superior** instalado en el sistema.
2. **Auriculares estéreo** (imprescindibles para percibir la espacialización acústica 3D: diferencias interaurales de tiempo ITD, diferencias de nivel ILD y filtrado de pabellón auricular).
3. **Librerías de Python**:
   - `sounddevice` (reproducción de audio en tiempo real)
   - `numpy` (cálculo matricial y generación de ondas)
   - `scipy` (procesamiento digital de señales y filtros acústicos)
   - `tkinter` (interfaz gráfica de usuario, incluida por defecto en la mayoría de instalaciones de Python)

---

## 🐧 Instrucciones de Instalación y Ejecución en Linux

### 1. Clonar el repositorio y entrar a la carpeta
```bash
git clone <URL_DEL_REPOSITORIO>
cd Videojuego-TCU-748
```

### 2. Verificar soporte de Tkinter (en distribuciones basadas en Debian / Ubuntu)
```bash
sudo apt update
sudo apt install python3-tk
```

### 3. Crear y activar un entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```
*(O si tienes `make`: `make install`)*

### 5. Ejecutar el juego
Puedes ejecutarlo directamente con Python:
```bash
python3 main.py
```
O utilizando el script de ejecución rápida o make:
```bash
./jugar.sh
# o: make run
```

---

## 🪟 Instrucciones de Instalación y Ejecución en Windows

### 1. Clonar o descargar el repositorio
Descarga el repositorio como archivo ZIP y extráelo, o clónalo usando Git:
```cmd
git clone <URL_DEL_REPOSITORIO>
cd Videojuego-TCU-748
```

### 2. Instalar las dependencias
En Windows tienes dos formas sencillas:
- **Opción A (Recomendada):** Haz **doble clic** sobre el archivo:
  ```cmd
  instalar.bat
  ```
- **Opción B (Por consola):** Abre CMD o PowerShell y ejecuta:
  ```cmd
  pip install -r requirements.txt
  ```

> **Nota:** En Windows, la librería gráfica `tkinter` ya viene instalada por defecto con el instalador oficial de Python.

### 3. Iniciar el juego
- **Opción A:** Haz **doble clic** sobre el archivo:
  ```cmd
  jugar.bat
  ```
- **Opción B:** Desde la consola ejecuta:
  ```cmd
  python main.py
  ```

---

## 🎮 Controles del Videojuego

Los controles se ejecutan directamente en la ventana de la aplicación:

| Tecla | Acción |
| :--- | :--- |
| **W** / **▲** | Avanzar un paso hacia el frente |
| **S** / **▼** | Retroceder un paso |
| **A** / **◀** | Girar 90° hacia la izquierda |
| **D** / **▶** | Girar 90° hacia la derecha |
| **ESPACIO** / **E** / **ENTER** | Interactuar con el objeto que tienes de frente |
| **L** / **P** | Escuchar un pulso acústico 3D de todo el entorno |

---

## 📁 Estructura del Proyecto

```text
├── main.py                    # Punto de entrada principal que arranca la interfaz gráfica
├── config.py                  # Parámetros globales: frecuencia de muestreo, límites de la sala
├── requirements.txt           # Lista de dependencias de Python
├── jugar.sh                   # Script de ejecución para Linux
├── jugar.bat                  # Script de ejecución con doble clic para Windows
├── .gitignore                 # Exclusiones de Git (caché, entornos virtuales)
├── README.md                  # Manual e instrucciones del proyecto
│
├── ui/                        # Interfaz gráfica (Tkinter)
│   ├── __init__.py
│   └── visualizer.py          # Pantalla de bienvenida, juego inmersivo y finalización
│
├── audio/                     # Motor acústico y sintetizador
│   ├── __init__.py
│   ├── hrtf_engine.py         # Motor HRTF 3D (cálculo de ITD, ILD, pinna, distancia y reverberación)
│   ├── sound_generator.py     # Síntesis matemática de efectos sonoros y cargador WAV
│   ├── mixer.py               # Mezclador thread-safe con cerrojo para sounddevice
│   └── assets/                # Efectos de sonido en formato WAV
│
├── game/                      # Lógica de juego y niveles
│   ├── __init__.py
│   ├── player.py              # Cinemática del jugador, posición (x, y) y dirección
│   ├── sound_object.py        # Objetos sonoros emisores con cálculo espacial relativo
│   ├── level_1.py             # Configuración del tutorial / Nivel 1 (teléfono, radio, puerta)
│   ├── narrator.py            # Emisor de mensajes de pantalla y sonidos prioritarios
│   └── game_loop.py           # Motor de coordinación de lógica e interacciones
│
└── input/                     # Módulo auxiliar de entrada
    ├── __init__.py
    └── controls.py            # Mapeo de teclas y acciones
```

---

## 🛠️ Modo de Pruebas Visuales (Depuración)

Por diseño accesible, el juego corre en pantalla oscura. Si en el futuro deseas reactivar el mapa 2D en tiempo real con las posiciones, flechas de orientación y distancias en metros para pruebas técnicas:

1. Abre el archivo [`ui/visualizer.py`](ui/visualizer.py).
2. Cambia la variable:
   ```python
   DEBUG_VISUAL_MODE = True
   ```
3. Guarda el archivo y ejecuta nuevamente el juego.

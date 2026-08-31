# Ecos en la Estación
### Videojuego Accesible basado en Audio Espacial 3D (HRTF)

**TCU-748: Tecnoinclusión**  
**Universidad de Costa Rica (UCR)**  
**Autores:** Marvin Coto Jiménez y Brandon Jiménez Campos  

---

## Descripción del Proyecto

**Ecos en la Estación** es un prototipo de videojuego de exploración accesible basado en **Audio Espacial 3D** mediante técnicas de **HRTF** (*Head-Related Transfer Function*), diseñado para personas no videntes y experiencias inmersivas auditivas.

---

## Requisitos Previos

1. **Python 3.8 o superior**.
2. **Auriculares estéreo** (imprescindibles para percibir la espacialización acústica 3D).
3. **Librerías de Python**:
   - `sounddevice` (reproducción de audio en tiempo real)
   - `numpy` (cálculo matricial y generación de señales)
   - `scipy` (procesamiento digital de señales y filtros acústicos)
   - `tkinter` (interfaz gráfica del sistema)

---

## Instrucciones de Instalación y Ejecución en Linux

### 1. Clonar el repositorio y acceder al directorio
```bash
git clone https://github.com/jmnzzz210/Videojuego-TCU-748
cd Videojuego-TCU-748
```

### 2. Instalación de soporte Tkinter (distribuciones basadas en Debian / Ubuntu)
```bash
sudo apt update
sudo apt install python3-tk
```

### 3. Creación y activación del entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalación de dependencias
```bash
pip install -r requirements.txt
```

### 5. Ejecución del videojuego
```bash
python3 main.py
```

---

## Instrucciones de Instalación y Ejecución en Windows

### 1. Obtención del repositorio
Descargar el repositorio en formato ZIP y descomprimir, o clonar mediante Git:
```cmd
git clone https://github.com/jmnzzz210/Videojuego-TCU-748
cd Videojuego-TCU-748
```

### 2. Ejecución de la aplicación
- **Método automático:**
  Ejecutar mediante doble clic el archivo:
  ```cmd
  jugar.bat
  ```
  *(El script comprueba la presencia de las dependencias requeridas, realiza la instalación en caso de ausencia e inicia el programa).*

- **Método manual por consola:**
  ```cmd
  pip install -r requirements.txt
  python main.py
  ```

---

## Controles del Videojuego

La captura de entradas se efectúa directamente en la ventana de la aplicación:

| Tecla | Acción |
| :--- | :--- |
| **W** / **Flecha Arriba** | Avanzar |
| **S** / **Flecha Abajo** | Retroceder |
| **A** / **Flecha Izquierda** | Girar 90° a la izquierda |
| **D** / **Flecha Derecha** | Girar 90° a la derecha |
| **ESPACIO** / **E** / **ENTER** | Interactuar con el objeto situado al frente |
| **L** / **P** | Emitir pulso acústico 3D para sondeo del entorno |

---

## Estructura del Proyecto

```text
├── main.py                    # Punto de entrada principal e inicio de la interfaz gráfica
├── config.py                  # Parámetros del sistema: frecuencia de muestreo y dimensiones
├── requirements.txt           # Especificación de dependencias de Python
├── jugar.bat                  # Script de ejecución para Windows
├── .gitignore                 # Exclusiones de control de versiones
├── README.md                  # Documentación técnica del proyecto
│
├── ui/                        # Interfaz gráfica (Tkinter)
│   ├── __init__.py
│   └── visualizer.py          # Ventanas de bienvenida, ejecución inmersiva y finalización
│
├── audio/                     # Motor acústico y procesamiento digital de señales
│   ├── __init__.py
│   ├── hrtf_engine.py         # Procesamiento HRTF (ITD, ILD, pinna, atenuación y reverberación)
│   ├── sound_generator.py     # Síntesis matemática de formas de onda y lectura WAV
│   ├── mixer.py               # Mezclador con control de concurrencia para sounddevice
│   └── assets/                # Archivos de audio en formato WAV
│
├── game/                      # Lógica de juego y estados
│   ├── __init__.py
│   ├── player.py              # Cinemática, coordenadas espaciales y dirección del jugador
│   ├── sound_object.py        # Definición de emisores acústicos y parámetros relativos
│   ├── level_1.py             # Configuración del tutorial (teléfono, radio y puerta)
│   ├── narrator.py            # Emisión de eventos y mensajes sonoros prioritarios
│   └── game_loop.py           # Coordinación de la lógica interactiva
│
└── input/                     # Módulo auxiliar de entrada
    ├── __init__.py
    └── controls.py            # Definición de acciones y constantes de entrada
```

---


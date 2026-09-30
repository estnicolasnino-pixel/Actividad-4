# Actividad-4
# Real-Time Gesture-Controlled Lighting System via ESP32 & MediaPipe

Este proyecto implementa un sistema de control de iluminación en tiempo real basado en visión por computador y comunicación serial. Mediante el uso de **OpenCV** y **MediaPipe** en una PC, se detectan gestos manuales a través de una cámara web y se envían comandos de control a una placa **ESP32** programada en **MicroPython**, la cual gestiona salidas físicas de iluminación LED (incluyendo control por modulación por ancho de pulsos - PWM y secuencias).

---

##  Arquitectura del Sistema

El flujo de trabajo del proyecto se divide en dos módulos principales:

1. **Módulo PC (Visión & Procesamiento):**
   - Captura de video en tiempo real vía OpenCV.
   - Extracción de puntos de referencia de la mano (*landmarks*) y clasificación de gestos utilizando el modelo `Gesture Recognizer` de MediaPipe.
   - Mapeo de gestos a comandos numéricos (`'1'` a `'5'`).
   - Envío de comandos a través del puerto serie (`pyserial`) a 115200 baudios.

2. **Módulo ESP32 (Embedded Control):**
   - Recepción continua de caracteres por transmisión serial asíncrona (`sys.stdin`).
   - Control de intensidad luminosa (PWM) en el LED principal (GPIO 12).
   - Activación de secuencias numéricas y patrones de conmutación en LEDs secundarios (GPIO 13 y GPIO 14).

---

##  Hardware y Conexiones

| Componente | Conexión / Pin ESP32 | Descripción |
| :--- | :--- | :--- |
| **ESP32 DevKit** | USB / Puerto COM | Interfaz de comunicación con PC |
| **LED 1 (PWM)** | GPIO 12 | Control de brillo por pulso |
| **LED 2** | GPIO 13 | Indicador / Secuencia 1 |
| **LED 3** | GPIO 14 | Indicador / Secuencia 2 |
| **GND** | GND | Tierra común del circuito |

---

##  Estructura del Repositorio

```text
├── app_pc.py                # Script de Python para procesamiento de imagen y envío serial
├── main.py                  # Script en MicroPython ejecutado en la ESP32
├── gesture_recognizer.task  # Modelo preentrenado de MediaPipe para reconocimiento de gestos
└── README.md                # Documentación del proyecto

import os
import urllib.request
import cv2
import time
import serial
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ------------------------------------------------------------------
# 1. Verificación e Instalación Automática del Modelo de MediaPipe
# ------------------------------------------------------------------
MODEL_PATH = 'gesture_recognizer.task'
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'

if not os.path.exists(MODEL_PATH):
    print("Descargando el modelo de MediaPipe Gesture Recognizer...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Modelo descargado exitosamente.")

# ------------------------------------------------------------------
# 2. Configuración del Puerto Serial (ESP32)
# ------------------------------------------------------------------
# Cambia 'COM3' al puerto asignado a tu ESP32 en Windows
SERIAL_PORT = 'COM5'  # Cámbialo según el Administrador de dispositivos
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"Conexión serial establecida en {SERIAL_PORT}.")
except Exception as e:
    print(f"Advertencia: No se pudo conectar al puerto serial {SERIAL_PORT}.")
    print(f"Detalle: {e}")
    print("El programa continuará en modo de simulación de cámara.")
    ser = None

# ------------------------------------------------------------------
# 3. Inicialización del Detector de Gestos
# ------------------------------------------------------------------
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.GestureRecognizerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE
)
recognizer = vision.GestureRecognizer.create_from_options(options)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se puede acceder a la cámara web.")
    exit()

last_cmd = ""

print("\n--- Sistema de Control de Gestos Iniciado ---")
print("Presiona la tecla 'q' sobre la ventana del video para salir.\n")

# ------------------------------------------------------------------
# 4. Bucle Principal de Captura y Procesamiento
# ------------------------------------------------------------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Espejar la imagen horizontalmente para vista natural
    frame = cv2.flip(frame, 1)

    # Convertir BGR a RGB para MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Reconocer gesto en la imagen actual
    recognition_result = recognizer.recognize(mp_image)

    cmd = "NONE"
    gesture_name = "Ninguno"

    if recognition_result.gestures:
        top_gesture = recognition_result.gestures[0][0]
        gesture_name = top_gesture.category_name

        # Mapeo de gestos según la guía
        if gesture_name == "Closed_Fist":
            cmd = '1'  # 30% Intensidad
        elif gesture_name == "Victory":
            cmd = '2'  # 70% Intensidad
        elif gesture_name == "Open_Palm":
            cmd = '3'  # 100% Intensidad
        elif gesture_name == "Thumb_Down":
            cmd = '4'  # Secuencia Modo 1 (Primera Interrupción)
        elif gesture_name == "Thumb_Up":
            cmd = '5'  # Secuencia Modo 2 (Segunda Interrupción)

        # Enviar comando solo si hubo un cambio respecto al último
        if cmd != "NONE" and cmd != last_cmd:
            last_cmd = cmd
            if ser and ser.is_open:
                ser.write(cmd.encode())
                print(f"[SERIAL -> ESP32] Comando enviado: '{cmd}' | Gesto: {gesture_name}")
            else:
                print(f"[SIMULACIÓN] Gesto detectado: '{cmd}' | Gesto: {gesture_name}")

    # Visualización de información en pantalla
    cv2.putText(frame, f"Gesto: {gesture_name}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    cv2.putText(frame, f"Comando: {last_cmd if last_cmd else 'Ninguno'}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)

    cv2.imshow('Control de Iluminacion - MediaPipe', frame)

    # Salir al presionar 'q' sobre la ventana de la cámara
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ------------------------------------------------------------------
# 5. Limpieza de Recursos
# ------------------------------------------------------------------
cap.release()
if ser and ser.is_open:
    ser.close()
cv2.destroyAllWindows()

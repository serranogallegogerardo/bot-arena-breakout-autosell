import pyautogui
import cv2
import os
from ultralytics import YOLO
from PIL import Image

# Definir las coordenadas para la captura de pantalla
x1, y1 = 1124, 182  # Coordenada superior izquierda
x2, y2 = 1762, 974  # Coordenada inferior derecha
width = x2 - x1
height = y2 - y1

# Capturar la pantalla en las coordenadas especificadas
screenshot = pyautogui.screenshot(region=(x1, y1, width, height))

# Guardar la captura de pantalla temporalmente
screenshot_path = 'captura_temporal.png'
screenshot.save(screenshot_path)

# Cargar la captura de pantalla con OpenCV
image = cv2.imread(screenshot_path)

# Cargar modelo YOLOv8 preentrenado
model = YOLO('yolov8n.pt')  # O puedes usar un modelo entrenado por ti

# Carpeta de salida para guardar los ítems recortados
output_folder = 'itemsGen'
os.makedirs(output_folder, exist_ok=True)

# Usar YOLO para detectar objetos en la captura
results = model(image)

# Verificar si hay detecciones
if results[0].boxes:  # Revisa si hay cajas detectadas
    # Iterar sobre los objetos detectados y guardarlos como PNG
    for idx, box in enumerate(results[0].boxes):  # results[0].boxes tiene las detecciones
        x_min, y_min, x_max, y_max = map(int, box.xyxy[0])  # Coordenadas de la caja

        # Recortar el objeto detectado
        item_img = image[y_min:y_max, x_min:x_max]

        # Convertir a formato PIL y guardar como PNG
        pil_img = Image.fromarray(cv2.cvtColor(item_img, cv2.COLOR_BGR2RGB))
        pil_img.save(f'{output_folder}/item_{idx}.png')

    print(f"Items detectados y guardados en {output_folder}")
else:
    print("No se detectaron objetos en la imagen.")

# Limpiar el archivo temporal
os.remove(screenshot_path)

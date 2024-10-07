import mss
import numpy as np
import cv2
import os

# Definir el área de la pantalla que quieres capturar (1127x142 hasta 1766x970)
x_start, y_start = 1127, 142
width, height = 1766 - 1127, 970 - 142  # Calcular el ancho y alto en base a las coordenadas

# Capturar la pantalla solo en la región definida
with mss.mss() as sct:
    monitor = {"top": y_start, "left": x_start, "width": width, "height": height}
    screenshot = sct.grab(monitor)

    # Convertir la imagen a un formato que OpenCV pueda usar (NumPy array)
    image = np.array(screenshot)

    # Convertir el formato de color de BGRA a BGR
    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicar suavizado para reducir el ruido (ajustado a un kernel más pequeño)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Detectar los bordes de los ítems usando el algoritmo de Canny (ajustar los umbrales)
    edges = cv2.Canny(blurred, 30, 120)

    # Encontrar los contornos en la imagen
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Crear la carpeta donde se guardarán los ítems
    output_dir = './itemsGen/'
    os.makedirs(output_dir, exist_ok=True)

    # Visualizar los contornos detectados para debugging
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    cv2.imshow("Contornos detectados", image)
    cv2.waitKey(0)

    # Procesar cada contorno (cada ítem detectado)
    for i, contour in enumerate(contours):
        # Ignorar contornos muy pequeños que podrían ser ruido (reducir el área mínima)
        if cv2.contourArea(contour) < 20:  # Reducido para capturar ítems más pequeños
            continue

        # Obtener el rectángulo delimitador para cada ítem (incluyendo los que ocupan varios cuadrados)
        x, y, w, h = cv2.boundingRect(contour)

        # Recortar la región del ítem
        item = image[y:y + h, x:x + w]

        # Guardar cada ítem como un archivo PNG
        item_filename = os.path.join(output_dir, f'item_{i}.png')
        cv2.imwrite(item_filename, item)
        print(f'Saved: {item_filename}')

    print("Todos los ítems han sido guardados correctamente.")

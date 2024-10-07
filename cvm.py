import cv2
import numpy as np
import mss
import pygetwindow as gw
import os
import time
import pyautogui  # Para simular clics del mouse
import random  # Para generar tiempos aleatorios

# Función para hacer clic en la posición del botón "Sell"
def click_sell_button(button_location):
    if button_location:
        pyautogui.moveTo(button_location[0], button_location[1])
        pyautogui.click(button='left')
        time.sleep(random.uniform(1, 3))
    else:
        print("No se encontró el botón Sell.")

# Captura solo la ventana del juego
def take_screenshot():
    window = gw.getWindowsWithTitle("Arena Breakout Infinite")[0]
    if window:
        left, top, right, bottom = window.left, window.top, window.right, window.bottom
        with mss.mss() as sct:
            monitor = {"top": top, "left": left, "width": right - left, "height": bottom - top}
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            return img, left, top
    else:
        print("Ventana no encontrada")
        return None, 0, 0

def find_item_position(item_image):
    if not os.path.exists(item_image):
        print(f"Error: El archivo {item_image} no se encontró.")
        return None
    screenshot, window_left, window_top = take_screenshot()
    if screenshot is None:
        return None
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    item = cv2.imread(item_image, 0)
    if item is None:
        print(f"Error al leer la imagen {item_image}")
        return None
    res = cv2.matchTemplate(screenshot_gray, item, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(f"Best match top left position: {max_loc}")
    print(f"Best match confidence: {max_val}")
    threshold = 0.5
    if max_val >= threshold:
        h, w = item.shape
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        return (center_x + window_left, center_y + window_top)
    else:
        return None

# Función para hacer clic derecho en una posición (x, y) y buscar el botón "Sell"
def right_click_and_find_sell_button(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click(button='right')
    time.sleep(random.uniform(1, 3))

    # Buscar el botón "Sell" hasta encontrarlo
    while True:
        button_location = find_item_position('./images/ItemSellButton.png')
        if button_location:
            print("Botón Sell encontrado. Haciendo clic.")
            click_sell_button(button_location)
            break  # Sale del bucle una vez que se encuentra el botón Sell
        else:
            print("Botón Sell no encontrado. Reintentando...")
            time.sleep(1)  # Esperar un segundo antes de volver a intentar

# Cargar automáticamente las imágenes de ítems desde la carpeta ./images/items/
item_list = [os.path.join('./images/items/', f) for f in os.listdir('./images/items/') if f.endswith(('.png', '.jpg', '.jpeg'))]

# Proceso de identificación, clic derecho y clic en el botón Sell
for item_image in item_list:
    loc = find_item_position(item_image)
    if loc is not None:
        print(f"Item {item_image} encontrado en posición {loc}")

        # Clic derecho y búsqueda del botón "Sell"
        right_click_and_find_sell_button(loc[0], loc[1])
    else:
        print(f"Item {item_image} no encontrado.")

import cv2
import numpy as np
import mss
import pygetwindow as gw
import os
import time
import pyautogui  # Para simular clics del mouse
import random  # Para generar tiempos aleatorios
import pyperclip  # Para manejar el portapapeles

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
    threshold = 0.7
    if max_val >= threshold:
        h, w = item.shape
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
        output_path = "output.png"
        cv2.imwrite(output_path, screenshot)
        print(f"Resultado guardado en {output_path}")
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        return (center_x + window_left, center_y + window_top)
    else:
        return None

# Función para hacer clic derecho en una posición (x, y) y buscar el botón "Sell"
def right_click_and_find_sell_button(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click(button='right')  # Clic derecho
    time.sleep(random.uniform(1, 3))  # Espera un tiempo aleatorio entre 1 y 3 segundos

# Función para obtener la lista de imágenes en una carpeta
def get_item_images(folder_path):
    valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    image_list = []
    for filename in os.listdir(folder_path):
        if any(filename.endswith(ext) for ext in valid_extensions):
            image_list.append(os.path.join(folder_path, filename))
    return image_list

def apply_percentage_to_price(price, percentage):
    discount = price * (percentage / 100)
    return price - discount

def main_process(percentage):
    # Paso 1: Clic en coordenadas 1480x220
    pyautogui.moveTo(1480, 220)
    pyautogui.click()

    # Paso 2: Clic en coordenadas 1445x790
    pyautogui.moveTo(1445, 790)
    pyautogui.click()

    # Paso 3: Ctrl + A y Ctrl + C para copiar el precio
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)  # Esperar un momento para asegurarse de que el precio esté copiado

    # Obtener el precio del portapapeles
    precio_copiado = pyperclip.paste()

    # Asegurarse de que el precio copiado sea un número
    try:
        precio = float(precio_copiado.replace(',', '').replace('$', '').strip())
    except ValueError:
        print("Error: No se pudo obtener un precio válido.")
        return

    # Calcular el nuevo precio con el descuento
    precio_con_descuento = apply_percentage_to_price(precio, percentage)

    # Copiar el nuevo precio al portapapeles
    pyperclip.copy(str(precio_con_descuento))

    # Paso 4: Ctrl + A y Ctrl + V para pegar el nuevo precio
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'v')

    # Paso 5: Clic en coordenadas 1406x908 (Confirmar el nuevo precio)
    pyautogui.moveTo(1406, 908)
    pyautogui.click()

if __name__ == "__main__":
    # Solicitar al usuario que ingrese el porcentaje de descuento solo una vez al inicio
    porcentaje = float(input("Ingresa el porcentaje de descuento (ejemplo: 10, 20, 30): "))

    # Lista de imágenes de ítems que quieres vender (todas las imágenes de la carpeta ./images/items/)
    item_list = get_item_images('./images/items/')

    # Proceso de identificación, clic derecho, ajuste de precio y luego pasar al siguiente ítem
    for item_image in item_list:
        loc = find_item_position(item_image)
        if loc is not None:
            print(f"Item {item_image} encontrado en posición {loc}")
            right_click_and_find_sell_button(loc[0], loc[1])

            # Realizar los pasos adicionales para copiar y pegar el precio con descuento
            main_process(porcentaje)

            # Aquí puedes agregar un pequeño retardo si es necesario para esperar antes de procesar el siguiente ítem
            time.sleep(5)
        else:
            print(f"Item {item_image} no encontrado.")

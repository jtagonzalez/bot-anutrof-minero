import pyautogui as heart
import cv2
import time
import random
import math
import tkinter as tk
import threading
import winsound
import numpy as np
import pyautogui
import heapq
import os
import re
_DIR = os.path.dirname(os.path.abspath(__file__))
import subprocess
from collections import deque
import pygetwindow as gw
import sys
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def pelear2():
    print("hola")
# ─────────────────────────────────────────────
# LOG A ARCHIVO — todos los print van a consola Y a bot_log.txt
# ─────────────────────────────────────────────
class _Tee:
    def __init__(self, filepath):
        self._file = open(filepath, 'a', encoding='utf-8')
        self._stdout = sys.__stdout__
        self._nueva_linea = True
    def write(self, msg):
        if self._nueva_linea and msg and msg != '\n':
            ts = time.strftime('[%Y-%m-%d %H:%M:%S] ')
            self._stdout.write(ts)
            self._file.write(ts)
        self._stdout.write(msg)
        self._file.write(msg)
        self._file.flush()
        self._nueva_linea = msg.endswith('\n')
    def flush(self):
        self._stdout.flush()
        self._file.flush()

_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot_log.txt')
sys.stdout = _Tee(_log_path)
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# FLAG DE REINICIO — señaliza al loop principal que reinicie el ciclo
# ─────────────────────────────────────────────
_bot_reiniciando = False
_dentro_de_reiniciar = False  # evita que recnec() llame reiniciar_juego() recursivamente

# ─────────────────────────────────────────────
# WATCHDOG — detecta inactividad real (5 min sin minar ni cambiar sala)
# ─────────────────────────────────────────────
_ultimo_progreso = time.time()

def registrar_progreso():
    global _ultimo_progreso
    _ultimo_progreso = time.time()

def _watchdog():
    while True:
        time.sleep(30)
        if time.time() - _ultimo_progreso > 300:
            print("⚠️ Watchdog: 5 min sin actividad real — reiniciando juego")
            reiniciar_juego()
            registrar_progreso()

threading.Thread(target=_watchdog, daemon=True).start()
# ─────────────────────────────────────────────

ventana = ["cerrar_ventanas.png","mapa.png"]

# ─────────────────────────────────────────────
# MONITOR DE VENTANA — hilo de fondo
# Si el juego pierde el foco por 15s, lo restaura automáticamente
# ─────────────────────────────────────────────
def _monitor_ventana():
    segundos_sin_juego = 0
    while True:
        time.sleep(1)
        try:
            ventana_activa = gw.getActiveWindow()
            es_juego = (
                ventana_activa is not None
                and 'dofus' in ventana_activa.title.lower()
                and 'ankama' not in ventana_activa.title.lower()
            )
            if es_juego:
                segundos_sin_juego = 0
            else:
                segundos_sin_juego += 1
                if segundos_sin_juego >= 15:
                    for title in gw.getAllTitles():
                        if ('dofus' in title.lower() or 'retro' in title.lower()) and 'ankama' not in title.lower():
                            wins = gw.getWindowsWithTitle(title)
                            if wins:
                                try:
                                    wins[0].restore()
                                    wins[0].activate()
                                    print("⚠️ Ventana del juego restaurada al frente")
                                except Exception:
                                    pass
                                break
                    segundos_sin_juego = 0
        except Exception:
            pass

threading.Thread(target=_monitor_ventana, daemon=True).start()
# ─────────────────────────────────────────────

_t_pixel_carga = None  # timestamp primera detección pixel (610,469) = pantalla de carga
_t_ultima_max_check = 0.0  # última vez que se comprobó si la ventana está maximizada

def _asegurar_ventana_maximizada():
    """Comprueba si la ventana del juego está maximizada; si no, la maximiza."""
    import win32gui, win32con
    import pygetwindow as gw
    try:
        for title in gw.getAllTitles():
            if ('dofus' in title.lower() or 'retro' in title.lower()) and 'ankama' not in title.lower():
                wins = gw.getWindowsWithTitle(title)
                if not wins:
                    continue
                hwnd = wins[0]._hWnd
                placement = win32gui.GetWindowPlacement(hwnd)
                # placement[1] == SW_SHOWMAXIMIZED (3) → ya está maximizada
                if placement[1] != win32con.SW_SHOWMAXIMIZED:
                    print(f"[recnec] ventana '{title}' no maximizada (showCmd={placement[1]}) — maximizando")
                    try:
                        forzar_foco(hwnd)
                        time.sleep(0.2)
                        pyautogui.hotkey('win', 'up')
                        time.sleep(0.5)
                    except Exception:
                        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                break
    except Exception as e:
        print(f"[recnec] _asegurar_ventana_maximizada error: {e}")

def recnec():
    global _t_pixel_carga, _t_ultima_max_check
    registrar_progreso()

    # Asegurar ventana maximizada (comprueba cada 5s para no ralentizar loops)
    ahora = time.time()
    if ahora - _t_ultima_max_check > 5.0:
        _t_ultima_max_check = ahora
        _asegurar_ventana_maximizada()
    #no cargo    
    if heart.pixelMatchesColor(990 , 734 , (255,  97,   0), tolerance=4) or heart.pixelMatchesColor(1236 , 902 , (255,  97,   0), tolerance=4) or heart.pixelMatchesColor(1237 , 943 ,(255,  97,   0), tolerance=4):
        print("activo aca")
        reiniciar_juego()

    # Detectar pantalla de carga prolongada: RGB (131,75,0) en (610,469) > 60s → reiniciar
    if heart.pixelMatchesColor(610, 469, (131, 75, 0), tolerance=15):
        if _t_pixel_carga is None:
            _t_pixel_carga = time.time()
            print(f"[recnec] pixel carga detectado en (610,469) — iniciando cuenta 60s")
        elif time.time() - _t_pixel_carga > 60:
            print(f"[recnec] pixel carga >60s ({time.time()-_t_pixel_carga:.0f}s) — reiniciando juego")
            _t_pixel_carga = None
            reiniciar_juego()
            return
    else:
        if _t_pixel_carga is not None:
            print(f"[recnec] pixel carga desapareció tras {time.time()-_t_pixel_carga:.0f}s")
        _t_pixel_carga = None

    while heart.pixelMatchesColor(488 , 722 , (254, 246,  65), tolerance=15) or heart.pixelMatchesColor(1036,694 , (255, 251, 226), tolerance=15) or heart.pixelMatchesColor(489, 722 ,(229, 221,  58), tolerance=15) or heart.pixelMatchesColor(1036 , 695, (230, 226, 204), tolerance=15) or heart.pixelMatchesColor(440,  411 ,(  6, 155, 216), tolerance=15):
        #no cargo
        if heart.pixelMatchesColor(990 , 734 , (255,  97,   0), tolerance=4) or heart.pixelMatchesColor(1236 , 902 , (255,  97,   0), tolerance=4) or heart.pixelMatchesColor(1237 , 943 ,(255,  97,   0), tolerance=4):
            print("no activo 2")
            reiniciar_juego()
        print("entra a reconectar")
        inicio_recnec = time.time()
        while True:
            #no cargo
            if heart.pixelMatchesColor(990 , 734 , (255,  97,   0), tolerance=4) or heart.pixelMatchesColor(1236 , 902 , (255,  97,   0), tolerance=4) or heart.pixelMatchesColor(1237 , 943 ,(255,  97,   0), tolerance=4):
                print("no activo 3")
                reiniciar_juego()
            if (time.time() - inicio_recnec) > 180:
                print("activa desde el tiempo de espera")
                print("⚠️ Reconexión fallida en 3 min — reiniciando juego desde cero")
                global _bot_reiniciando, _dentro_de_reiniciar
                _bot_reiniciando = True
                if _dentro_de_reiniciar:
                    print("⚠️ recnec falló dentro de reiniciar_juego — el reintento lo maneja reiniciar_juego")
                    return
                reiniciar_juego()
                return
            #cuentas certificada
            if heart.pixelMatchesColor(852,572, (255,  91,   0), tolerance=15):
                heart.click(856,579 )
                time.sleep(1)
            #cuentas certificada
            if heart.pixelMatchesColor(835, 604, (255,  97,   0), tolerance=15):
                heart.click(835, 604 )
                time.sleep(1)
            # cuentas registradas
            if heart.pixelMatchesColor(854,576 ,(242,  92,   0), tolerance=15):
                heart.click(779, 550)
                time.sleep(1)
            #inactivo
            if heart.pixelMatchesColor(779, 550, (253,  96,   0), tolerance=15):
                heart.click(779, 550)
                time.sleep(1)
            #inactivo
            if heart.pixelMatchesColor(787,  553 , (255,  97,   0), tolerance=15):
                heart.click(787,  553)
                time.sleep(1)
            #mantwnimieno    
            if heart.pixelMatchesColor(789,  555, (255,  97,   0), tolerance=15):
                heart.click(789,  555)
                time.sleep(1)    
            if heart.pixelMatchesColor(744 , 553,(236,  89,   0), tolerance=15):
                heart.click(744 , 553)
                time.sleep(1)
            if heart.pixelMatchesColor(677, 455,(208, 120,   0), tolerance=15):
                heart.click(677, 455)
                time.sleep(1)
            if heart.pixelMatchesColor(764,531, (253,  96,   0), tolerance=15):
                heart.click(764,531)
                time.sleep(1)
               
            if heart.pixelMatchesColor(779,565 , (255,  97,   0), tolerance=15):
                heart.click(779,565 )
                time.sleep(1)
            #server bun
            _pos_server = buscar_imagen_en_pantalla("sever2.png", region_busqueda=(0, 0, 1280, 1024))
            if _pos_server:
                heart.click(_pos_server[0], _pos_server[1], 2, interval=.2)
                time.sleep(1)
            #clic personaje
            if heart.pixelMatchesColor(478 ,568, (208, 200, 183), tolerance=15):
                heart.click(478,  568, 2, interval=.2 )
                time.sleep(1) 
                
            #equupo minero
            if heart.pixelMatchesColor(1043, 821,(102, 145, 255), tolerance=15):

                time.sleep(3)
                heart.click(1043, 821, 2, interval=.2 )
                print("sale de reconectar")
                break

            time.sleep(0.5)  # evitar que el loop queme los 20 intentos instantáneamente

def recnec2():
    if heart.pixelMatchesColor(772, 546, (255,  97,   0), tolerance=15) or heart.pixelMatchesColor(655,448,(220, 129,   0), tolerance=15) or heart.pixelMatchesColor(767 , 527 , (255,  97,   0), tolerance=15)  or heart.pixelMatchesColor(766, 556 , (255,  97,   0), tolerance=15) or heart.pixelMatchesColor(848, 560,(250,  95,   0), tolerance=15) or heart.pixelMatchesColor(774 , 557 ,(255,  97,   0), tolerance=15):
        print("entra a reconectar")
        intentos_recnec2 = 0
        inicio_recnec2 = time.time()
        while True:
            intentos_recnec2 += 1
            if intentos_recnec2 > 20 or (time.time() - inicio_recnec2) > 120:
                print("⚠️ recnec2: reconexión fallida — reiniciando juego desde cero")
                reiniciar_juego()
                return
            print("enrta al wile")
            if  heart.pixelMatchesColor(784 ,421 ,(255, 255, 255), tolerance=15) and heart.pixelMatchesColor(835, 540 ,(255,  97,   0), tolerance=15):
                time.sleep(1)
                heart.click(835, 540)
            if  heart.pixelMatchesColor(772, 546, (255,  97,   0), tolerance=15) or heart.pixelMatchesColor(655,448,(220, 129,   0), tolerance=15) or heart.pixelMatchesColor(767 , 527 , (255,  97,   0), tolerance=15) or heart.pixelMatchesColor(853 ,556 , (255,  97,   0), tolerance=15) or heart.pixelMatchesColor(851 , 576 ,(255,  97,   0), tolerance=15) or heart.pixelMatchesColor(777, 568, (255,  97,   0), tolerance=15) :
                print("encontrada")
                heart.click(767 , 527)
                time.sleep(1)
                heart.click(772, 547)
                time.sleep(1)
                heart.click(655, 448)
                time.sleep(1)
                heart.click(848, 560)
                time.sleep(1)
                heart.click(853 ,556)
                time.sleep(1)
                heart.click(851 , 576)
                time.sleep(1)
                heart.click(777, 568)
            
                break
            if heart.pixelMatchesColor(852, 562,(255,  97,   0), tolerance=15) :
                    while True:
                        if heart.pixelMatchesColor(852, 562,(255,  97,   0), tolerance=15) :
                            print("encontrada2.1")
                            heart.click(852, 562)
                            time.sleep(1)
                            heart.click(657, 448 )
                        if heart.pixelMatchesColor(702, 366,( 41,  38,  31), tolerance=15) and heart.pixelMatchesColor(690,  420, (6, 155, 216), tolerance=15):
                              break
                      

            if heart.pixelMatchesColor(702, 366,( 41,  38,  31), tolerance=15) and heart.pixelMatchesColor(690,  420, (6, 155, 216), tolerance=15):
                    print("encontrada2")
                    heart.moveTo(687, 429)
                    heart.click(clicks=2,interval=0.1)
                    
            if heart.pixelMatchesColor(763, 709,(236, 142,   2), tolerance=15) and heart.pixelMatchesColor(771, 667, (121, 111,  90), tolerance=15):
                    print("encontrada3")
                    heart.moveTo(477, 495)
                    heart.click(clicks=2,interval=0.1)
                        
            time.sleep(2)
            if heart.pixelMatchesColor(1184 , 635 , (176, 184, 147), tolerance=10) :    
                pelear2()
            if  heart.pixelMatchesColor(864, 727, (216,   1,   1), tolerance=15):
                    time.sleep(.5)
                    print("salio")
                    heart.click(142, 952 )
                    #pyautogui.write('/away', interval=0.25)
                    pyautogui.press("enter")
                    break
    return

def esperar_sala(condicion, timeout=80, con_recnec=False, reintento=None):
    """
    Espera hasta que condicion() sea True o se supere el timeout.
    Cada tick = 0.2s → timeout=80 equivale a 16 segundos máx.
    Si se pasa reintento (callable), lo ejecuta cada 7s mientras espera.
    Retorna True si la condición se cumplió, False si hubo timeout.
    """
    ticks_reintento = 35  # 35 × 0.2s = 7 segundos
    ticks_desde_ultimo = 0
    for _ in range(timeout):
        if con_recnec:
            recnec()
        inter()
        any_desk()
        time.sleep(.2)
        if condicion():
            return True
        if reintento:
            ticks_desde_ultimo += 1
            if ticks_desde_ultimo >= ticks_reintento:
                reintento()
                ticks_desde_ultimo = 0
    return False

def inter():
    if heart.pixelMatchesColor(808, 347, (( 81,  74,  60)), tolerance=10) and heart.pixelMatchesColor(738, 443 , (255,  97,   0), tolerance=10) and heart.pixelMatchesColor( 867, 442, (255,  97,   0), tolerance=10):
        time.sleep(1)
        heart.click(817, 485)
        time.sleep(.2)
        heart.click(32,  348)
        time.sleep(.2)
        heart.click(496,  681)

         
def detectar_enemigo_sala(imagen_enemigo, region_busqueda=(310, 132, 964, 580), umbral=0.5, debug=False):
    # Usar siempre la ruta base del script para archivos relativos
    if not os.path.isabs(imagen_enemigo):
        imagen_enemigo = os.path.join(_DIR, imagen_enemigo)
    if debug:
        print(f"[detectar_enemigo_sala] cargando imagen: {imagen_enemigo}")
    # Cargar plantilla en formato BGR de 3 canales
    template_enemigo = cv2.imread(imagen_enemigo, cv2.IMREAD_COLOR)
    if template_enemigo is None:
        raise ValueError(f"No se pudo cargar la imagen: {imagen_enemigo}")

    # Captura de pantalla
    screenshot = pyautogui.screenshot(region=region_busqueda)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Verifica que la plantilla sea más pequeña que la screenshot
    if (template_enemigo.shape[0] > screenshot.shape[0] or
        template_enemigo.shape[1] > screenshot.shape[1]):
        raise ValueError("La plantilla es más grande que la imagen de búsqueda.")

    # MatchTemplate
    resultado = cv2.matchTemplate(screenshot, template_enemigo, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(resultado)

    if max_val < umbral:
        return None

    w, h = template_enemigo.shape[1], template_enemigo.shape[0]
    x_abs = region_busqueda[0] + max_loc[0] + w // 2
    y_abs = region_busqueda[1] + max_loc[1] + h // 2
    return (x_abs, y_abs)
def reconectar():

    tiempo = 0
    

    #if heart.pixelMatchesColor(415, 211, (211, 179, 82), tolerance=5) or heart.pixelMatchesColor(415, 211, (234, 199, 91), tolerance=5):
        

    while not heart.pixelMatchesColor(921, 853, (213, 207, 170), tolerance=5):
        

        #cierra el juego y lo habre
        heart.hotkey('alt','f4')
        time.sleep(2)
        heart.hotkey('win','r')
        time.sleep(1)
        heart.write(r'"C:\Users\USUARIO\Desktop\Dofus Retro.lnk"')
        time.sleep(1)
        heart.press('enter')
        
        while True:   
            
            #espera a que cargue el juego y maximisa
            time.sleep(1)
            tiempo +=1
    
            if heart.pixelMatchesColor(453, 348, (93, 157, 189), tolerance=5) or tiempo >= 10:
                heart.click(940,210)
                time.sleep(2)
                tiempo=0
                break
            
            

        while not heart.pixelMatchesColor(842, 716, (236, 142, 2), tolerance=5):
            
            time.sleep(1)
            tiempo +=1

            #selecciona server bun
            if heart.pixelMatchesColor(523, 427, (6, 155, 216), tolerance=5) :
                heart.doubleClick(522,425)
                time.sleep(2)
            if tiempo >= 10:
                tiempo=0
                break
            

        #seleeciona el personaje y espera
        while True:
    
            time.sleep(1)
            tiempo +=1
    
            if heart.pixelMatchesColor(842, 716, (236, 142, 2), tolerance=5):
                heart.doubleClick(477,540)
                time.sleep(2)
            
            if heart.pixelMatchesColor(921, 853, (213, 207, 170), tolerance=5) or tiempo >= 15:
                tiempo=0
                break

        #detecta si esá en pelea
        if heart.pixelMatchesColor(1267,627,(230,33,30), tolerance=10):
            heart.click(1257,827)
            time.sleep(0.5)
            heart.click(1256,783)
            pelear2()

        else:
            pass 
        
    # se sube al pavo
    heart.hotkey('shift','d')
    time.sleep(0.5)
def buscar_imagen_en_inventario(imagen, region_busqueda=(0, 0, 1280,1024 ), umbral=0.5):
    # Usar la ruta del script para archivos relativos
    if not os.path.isabs(imagen):
        imagen = os.path.join(_DIR, imagen)
    # Cargar imagen de plantilla en BGR (ignorar canal alfa)
    template = cv2.imread(imagen, cv2.IMREAD_COLOR)
    if template is None:
        print(f"Error: No se pudo cargar la imagen {imagen}")
        return None

    # Capturar región de pantalla
    screenshot = pyautogui.screenshot(region=region_busqueda)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Validar tamaños compatibles
    if template.shape[0] > screenshot.shape[0] or template.shape[1] > screenshot.shape[1]:
        print("Error: La plantilla es más grande que la región de búsqueda.")
        return None

    # Asegurarse que ambas imágenes tengan el mismo número de canales (3)
    if template.shape[2] != screenshot.shape[2]:
        print("Error: Las imágenes tienen diferente número de canales.")
        return None

    # Match
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print("el humbral es  {max_val}")
    if max_val >= umbral:
        x, y = max_loc
        x += region_busqueda[0]
        y += region_busqueda[1]
        w, h = template.shape[1], template.shape[0]
        return x + w // 2, y + h // 2
    else:
        return None

def buscar_imagen_en_pantalla(imagen, region_busqueda=(310, 132, 964, 580), umbral=0.5):
    if not os.path.isabs(imagen):
        imagen = os.path.join(_DIR, imagen)

    # Cargar la imagen de referencia
    template = cv2.imread(imagen, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"Error: No se pudo cargar la imagen {imagen}")
        return None

    # Normalizar template a BGR (3 canales)
    if len(template.shape) == 2:
        template = cv2.cvtColor(template, cv2.COLOR_GRAY2BGR)
    elif template.shape[2] == 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    # Capturar la pantalla solo en la región de búsqueda
    screenshot = pyautogui.screenshot(region=region_busqueda)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Realizar la coincidencia de imágenes
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # Verificar si la confianza es suficiente
    if max_val >= umbral:
        x, y = max_loc
        x += region_busqueda[0]  # Ajustar a coordenadas absolutas
        y += region_busqueda[1]
        #print(f"Imagen encontrada en ({x}, {y}) con confianza {max_val}")
        # Mover el cursor al centro de la imagen encontrada
        w, h = template.shape[1], template.shape[0]
        #pyautogui.moveTo(x + w // 2, y + h // 2, duration=0.1)
        #print(f" pos real {x + w // 2, y + h // 2}")
        return x + w // 2, y + h // 2  # Retorna las coordenadas absolutas
    else:
        #print(f"No se encontró la imagen {imagen}")
        return None  # Retorna None si no la encuentra

def _score_imagen(ruta_template, screenshot_bgr):
    """Retorna (score, loc) de una template sobre un screenshot ya capturado. Score 0.0 si no carga."""
    if not os.path.isabs(ruta_template):
        ruta_template = os.path.join(_DIR, ruta_template)
    template = cv2.imread(ruta_template, cv2.IMREAD_UNCHANGED)
    if template is None:
        return 0.0, (0, 0)
    if len(template.shape) == 3 and template.shape[2] == 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
    res = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return max_val, max_loc
    
def _score_imagen_tmpl(template_bgr, screenshot_bgr):
    """Igual que _score_imagen pero recibe el template ya cargado en memoria (más rápido en loops)."""
    if template_bgr is None:
        return 0.0, (0, 0)
    res = cv2.matchTemplate(screenshot_bgr, template_bgr, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return max_val, max_loc

def enemigo_mas_lejano_al_aliado(imagen_enemigo, imagen_aliado, region_busqueda=(310, 132, 964, 580), umbral=0.5, debug=False):
    """
    Busca enemigos y un aliado en pantalla y retorna la posición del enemigo más lejano al aliado.

    Args:
        imagen_enemigo (str): Ruta a la imagen del enemigo.
        imagen_aliado (str): Ruta a la imagen del aliado.
        region_busqueda (tuple): Región (x, y, ancho, alto) para buscar.
        umbral (float): Umbral de coincidencia mínima.
        debug (bool): Imprime información extra si es True.

    Returns:
        tuple: Coordenadas (x, y) del enemigo más lejano al aliado, o None si no hay enemigos o no se encuentra al aliado.
    """
    # Cargar imágenes
    template_enemigo = cv2.imread(imagen_enemigo, cv2.IMREAD_UNCHANGED)
    template_aliado = cv2.imread(imagen_aliado, cv2.IMREAD_UNCHANGED)

    if template_enemigo is None or template_aliado is None:
        if debug:
            print("Error al cargar imágenes.")
        return None

    # Captura de pantalla
    screenshot = pyautogui.screenshot(region=region_busqueda)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Buscar aliado
    res_aliado = cv2.matchTemplate(screenshot, template_aliado, cv2.TM_CCOEFF_NORMED)
    _, max_val_aliado, _, max_loc_aliado = cv2.minMaxLoc(res_aliado)

    if max_val_aliado < umbral:
        if debug:
            print("Aliado no encontrado.")
        return None

    w_aliado, h_aliado = template_aliado.shape[1], template_aliado.shape[0]
    x_aliado = max_loc_aliado[0] + region_busqueda[0] + w_aliado // 2
    y_aliado = max_loc_aliado[1] + region_busqueda[1] + h_aliado // 2
    pos_aliado = (x_aliado, y_aliado)

    if debug:
        print(f"Aliado encontrado en {pos_aliado}")

    # Buscar enemigos
    res_enemigos = cv2.matchTemplate(screenshot, template_enemigo, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res_enemigos >= umbral)
    w_e, h_e = template_enemigo.shape[1], template_enemigo.shape[0]

    enemigos = []
    for pt in zip(*loc[::-1]):
        x = pt[0] + region_busqueda[0] + w_e // 2
        y = pt[1] + region_busqueda[1] + h_e // 2
        enemigos.append((x, y))
        if debug:
            print(f"Enemigo detectado en ({x}, {y})")

    if not enemigos:
        if debug:
            print("No se encontraron enemigos.")
        return None

    # Elegir el enemigo más lejano
    enemigo_lejano = max(enemigos, key=lambda e: math.dist(pos_aliado, e))
    
    if debug:
        print(f"Enemigo más lejano al aliado está en {enemigo_lejano}")

    return enemigo_lejano

def enemigo_mas_cercano_al_aliado(imagen_enemigo, imagen_aliado, region_busqueda=(310, 132, 964, 580), umbral=0.5, debug=False):
    
    # Cargar imágenes
    template_enemigo = cv2.imread(imagen_enemigo, cv2.IMREAD_UNCHANGED)
    template_aliado = cv2.imread(imagen_aliado, cv2.IMREAD_UNCHANGED)

    if template_enemigo is None or template_aliado is None:
        if debug:
            print("Error al cargar imágenes.")
        return None

    # Capturar pantalla en la región indicada
    screenshot = pyautogui.screenshot(region=region_busqueda)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Buscar aliado
    res_aliado = cv2.matchTemplate(screenshot, template_aliado, cv2.TM_CCOEFF_NORMED)
    _, max_val_aliado, _, max_loc_aliado = cv2.minMaxLoc(res_aliado)

    if max_val_aliado < umbral:
        if debug:
            print("Aliado no encontrado.")
        return None

    w_aliado, h_aliado = template_aliado.shape[1], template_aliado.shape[0]
    x_aliado = max_loc_aliado[0] + region_busqueda[0] + w_aliado // 2
    y_aliado = max_loc_aliado[1] + region_busqueda[1] + h_aliado // 2
    pos_aliado = (x_aliado, y_aliado)

    if debug:
        print(f"Aliado encontrado en {pos_aliado}")

    # Buscar enemigos
    res_enemigos = cv2.matchTemplate(screenshot, template_enemigo, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res_enemigos >= umbral)
    w_e, h_e = template_enemigo.shape[1], template_enemigo.shape[0]

    enemigos = []
    for pt in zip(*loc[::-1]):
        x = pt[0] + region_busqueda[0] + w_e // 2
        y = pt[1] + region_busqueda[1] + h_e // 2
        enemigos.append((x, y))
        if debug:
            print(f"Enemigo detectado en ({x}, {y})")

    if not enemigos:
        if debug:
            print("No se encontraron enemigos.")
        return None

    # Buscar enemigo más cercano
    enemigo_cercano = min(enemigos, key=lambda e: math.dist(pos_aliado, e))
    
    if debug:
        print(f"Enemigo más cercano al aliado está en {enemigo_cercano}")

    return enemigo_cercano
def calcular_distancia(pos1, pos2):
    # Calcula la distancia euclidiana entre dos puntos
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

def caminar3(umbral,umbral2):
    
    x1 = None
    distancia=260
    sx2, sy2 = 841, 421
    dx,dy = 900,600

    try : 
       
       x1,y1= buscar_imagen_en_pantalla2(sadi)
       print(f"posicion de aliado es {x1,y1}")
       

       
       x2,y2= buscar_imagen_en_pantalla2(jala)
       print(f"posicion de aliado es {x2,y2}")
       distancia = calcular_distancia((x1, y1), (x2, y2))
       
       sx2,sy2 = x2,y2
       
    
    except TypeError:
       pass
       

    try:
        dx = x2 - x1 
        dy = y2 - y1
    
    except UnboundLocalError:
        pass
    """des = 0
    if distancia <= 50:
       heart.press('5')
       time.sleep(0.7)
       heart.click(x2,y2)
       time.sleep(1)
       heart.press('6')
       time.sleep(0.7)
       heart.click(x2,y2)
       time.sleep(1)
       des = 1"""
    

    if distancia >= 0 and x1 is not None and heart.pixelMatchesColor(345 ,215 , (255, 255, 255)):
       print("entra al promer if")          
          
       
           
       if dx > 0 and dy > 0:
           print("Arrib a la izquierda nuevo")
           heart.click(x1-130,y1-70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-130,y1-35,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-130,y1,clicks=2,interval=.1) 
           time.sleep(.1) 
           heart.click(x1-130,y1+35,clicks=2,interval=.1)
           time.sleep(.1)
           heart.click(x1-130,y1+70,clicks=2,interval=.1)

           heart.click(x1-130,y1-70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-75,y1-70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-5,y1-70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1+60,y1-70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1+130,y1-70,clicks=2,interval=.1)

           """heart.click(x1+130,y1+51,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1+65,y1+51,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1,y1+51,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1-65,y1+51,clicks=2,interval=.2) 
           
           heart.click(x1+130,y1+52,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1+130,y1+18,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1+130,y1-18,clicks=2,interval=.2) 
           time.sleep(.1) 
           heart.click(x1+130,y1-55,clicks=2,interval=.2)"""
           
           
       elif dx > 0 and dy < 0:
           print("abajo a la izquierda nuevo")
           heart.click(x1-135,y1+70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-135,y1+35,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-135,y1,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1-135,y1-35,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-135,y1-70,clicks=2,interval=.1) 
           time.sleep(.1)#Arriba a la derecha"

           
           heart.click(x1-135,y1+70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-70,y1+70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-5,y1+70,clicks=2,interval=.1) 
           time.sleep(.1) 
           heart.click(x1+60,y1+70,clicks=2,interval=.1)
           time.sleep(.1) 
           heart.click(x1+125,y1+70,clicks=2,interval=.1)

           """heart.click(x1+135,y1-70,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1+70,y1-70,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1+5,y1-70,clicks=2,interval=.2) 
           time.sleep(.1) 
           heart.click(x1-65,y1-70,clicks=2,interval=.2) 
           
           heart.click(x1+135,y1-70,clicks=2,interval=.2)  
           time.sleep(.1)
           heart.click(x1+105,y1-35,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1+105,y1,clicks=2,interval=.2) 
           time.sleep(.1)
           heart.click(x1+105,y1+35,clicks=2,interval=.2)"""
       elif dx < 0 and dy > 0:
           print("Arriba a la derecha nuevo")
           heart.click(x1+135,y1-70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1+70,y1-70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1+5,y1-70,clicks=2,interval=.1) 
           time.sleep(.1) 
           heart.click(x1-65,y1-70,clicks=2,interval=.1) 
           time.sleep(.1) 
           heart.click(x1-130,y1-70,clicks=2,interval=.1) 
           
           heart.click(x1+135,y1-70,clicks=2,interval=.1)  
           time.sleep(.1)
           heart.click(x1+135,y1-35,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1+135,y1,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1+135,y1+35,clicks=2,interval=.1)
           time.sleep(.1)
           heart.click(x1+135,y1+70,clicks=2,interval=.1)
       elif dx < 0 and dy < 0:
           print("Abajo a la derecha nuevo")
           
           heart.click(x1+130,y1+70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1+65,y1+70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1,y1+70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-65,y1+70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1-130,y1+70,clicks=2,interval=.1)
           
           heart.click(x1+130,y1+70,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1+130,y1+35,clicks=2,interval=.1) 
           time.sleep(.1)
           heart.click(x1+130,y1,clicks=2,interval=.1) 
           time.sleep(.1) 
           heart.click(x1+130,y1-35,clicks=2,interval=.1)
           time.sleep(.1) 
           heart.click(x1+130,y1-70,clicks=2,interval=.1)
           if not heart.pixelMatchesColor(1188, 633,(  0, 153,   0), tolerance=10):
               heart.click(1188, 633)
       
       heart.moveTo(1272,754)
       time.sleep(0.5)
    print(distancia)
def enemigo_mas_cercano_al_aliado2(lista_enemigo, lista_aliado,
                                   region_busqueda=(310, 132, 964, 580), 
                                   umbral=0.5, debug=False):

    # ---------------------------
    # Capturar screenshot en 3 canales (BGR)
    # ---------------------------
    screenshot = np.array(pyautogui.screenshot(region=region_busqueda))
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # ---------------------------
    # Función interna para cargar imágenes y convertir RGBA → BGR
    # ---------------------------
    def cargar_template(ruta):
        img = cv2.imread(ruta, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"[ERROR] No se pudo cargar {ruta}")
            return None

        # Si tiene canal alpha, convertir a 3 canales
        if len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img

    # ---------------------------
    # Buscar aliado (usando lista de imágenes)
    # ---------------------------
    pos_aliado = None
    mejor_val_aliado = 0

    for img_aliado in lista_aliado:

        template_aliado = cargar_template(img_aliado)
        if template_aliado is None:
            continue

        res = cv2.matchTemplate(screenshot, template_aliado, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val > umbral and max_val > mejor_val_aliado:
            mejor_val_aliado = max_val

            w, h = template_aliado.shape[1], template_aliado.shape[0]
            pos_aliado = (max_loc[0] + region_busqueda[0] + w // 2,
                          max_loc[1] + region_busqueda[1] + h // 2)

            if debug:
                print(f"[ALIADO] Detectado {img_aliado} en {pos_aliado} val={max_val}")

    if pos_aliado is None:
        if debug:
            print("[ALIADO] No se encontró ningún aliado.")
        return (555,555) # <-- fallback solicitado

    # ---------------------------
    # Buscar enemigos (usando lista de imágenes)
    # ---------------------------
    enemigos_detectados = []

    for img_enemigo in lista_enemigo:

        template_enemigo = cargar_template(img_enemigo)
        if template_enemigo is None:
            continue

        res = cv2.matchTemplate(screenshot, template_enemigo, cv2.TM_CCOEFF_NORMED)
        _, max_val_e, _, max_loc_e = cv2.minMaxLoc(res)

        if max_val_e < umbral:
            continue

        w, h = template_enemigo.shape[1], template_enemigo.shape[0]
        x = max_loc_e[0] + region_busqueda[0] + w // 2
        y = max_loc_e[1] + region_busqueda[1] + h // 2
        enemigos_detectados.append((x, y))

        if debug:
            print(f"[ENEMIGO] {img_enemigo} en {(x, y)} val={max_val_e:.2f}")

    if not enemigos_detectados:
        if debug:
            print("[ENEMIGO] No se encontró ningún enemigo.")
        return (555,555)

    # ---------------------------
    # Buscar enemigo más cercano al aliado
    # ---------------------------
    enemigo_cercano = min(enemigos_detectados, key=lambda e: math.dist(pos_aliado, e))

    if debug:
        print(f"[RESULTADO] Enemigo más cercano: {enemigo_cercano}")

    return enemigo_cercano

def modificarinventario():
    if not heart.pixelMatchesColor(1017,423, (255, 255, 255), tolerance=5) or not heart.pixelMatchesColor(592,423 , (253, 253, 253), tolerance=5):
        heart.click(854,453)

def pelear3():
    print(" empieza con el ciclo de pelea numero 2")
    forma=False
    modo = 'combate'
    contador=0
    turno =0
    
    if heart.pixelMatchesColor(1184 , 635 , (176, 184, 147), tolerance=10) or  heart.pixelMatchesColor(1264,623 , (255,  33,  33), tolerance=10):
        """or heart.pixelMatchesColor(852, 817 , (255, 142,   0), tolerance=5)"""
        #-and modo == 'combate' and heart.pixelMatchesColor(1263,625,(255,  33,  33), tolerance=10)
        time.sleep(1)
        print("entra a pelear en el if a hacer todo")
        print(" empieza con el ciclo de pelea numero 2 adentro")
        #heart.click(1257,  812, clicks=2,interval=.2)
        #time.sleep(.5)
        print("antes de dar clcick")
        
        heart.click(1003,490,clicks=2,interval=.2)
        heart.click(1112, 817, clicks=10,interval=.2)
        time.sleep(.3)
        """heart.click(1080,  816, clicks=2,interval=.2)
        time.sleep(.5)"""
        #heart.click(1255,  776, clicks=2,interval=.2)
        
        time.sleep(.3)
        heart.moveTo(1272,754)
        if not heart.pixelMatchesColor(1190, 630,(0,153,0), tolerance=5):
            heart.click(1190, 630)
        
        heart.press('space')
        time.sleep(3)
        """heart.keyUp('e')"""
        #activa modo criatura y combate
        if heart.pixelMatchesColor(968, 818,(255,102,0), tolerance=10) and forma==False and modo == 'combate': 
        #modo tactico
            if not heart.pixelMatchesColor(1187, 621,(0,153,0), tolerance=5):
                heart.click(1187, 621)
                time.sleep(0.5)
                #circulo de pelea
            if not heart.pixelMatchesColor(1212, 630,(0,153,0), tolerance=5):  
                heart.click(1212,630)  
                time.sleep(0.5)
            #ocultar reto
            if heart.pixelMatchesColor(354, 212,(255,255,255), tolerance=5):  
                heart.click(354, 212)  
                time.sleep(0.5) 
                heart.moveTo(1272,754)  
             
        
        #espectador
            if not heart.pixelMatchesColor(1237, 631,(0,153,0), tolerance=5):  
                heart.click(1237,635)  
                
                time.sleep(0.5) 

    #boucle paa esperar turno
        heart.moveTo(1272,754)
        print("antes de empezar el ciclo")
        #while heart.pixelMatchesColor(1263 ,  624 ,(255,  33,  33) , tolerance=10) and modo == 'combate'
        while heart.pixelMatchesColor(1236 , 661 , (213, 170, 100), tolerance=10):
             heart.moveTo(1272,754)
             time.sleep(0.3)  

             print("comie|nza ciclo pelea 3")
             recnec()
             if not heart.pixelMatchesColor(1188, 619, (  0, 153,   0), tolerance=5):
                heart.click(1187, 621)
                heart.moveTo(1272,754)
                time.sleep(0.5)
                print("entra a quitar modo tatico")
             

             if not heart.pixelMatchesColor(1263 ,  624 ,(255,  33,  33) , tolerance=10) : 
                 print("entra a romper")
                 break
             # detecta si es miturno     
             if heart.pixelMatchesColor(888,726,(255,102,0), tolerance=10) and heart.pixelMatchesColor(354, 212, (255,255,255), tolerance=5)  and modo == 'combate':    
                 time.sleep(0.2)    
                 print("entra a turno") 
                 contador=0
                 
                 
                 
                 # cofre
                 if heart.pixelMatchesColor(1155 , 773 ,(121,  51,  55), tolerance=5) and modo == 'combate':
                


                    try:
                    #a,b =heart.locateCenterOnScreen('sacro.png', confidence=0.6, region=(988, 608, 289, 96))


                    #cofre
                     variente = 0
                    # c,u = enemigo_mas_cercano_al_aliado("ali-n.png",
                      #                                          "ali-n.png")
                     if heart.pixelMatchesColor(1155 , 773 ,(121,  51,  55), tolerance=5):
                          
                          
                          print("se tira cofre")
                          if heart.pixelMatchesColor(1202,424, (81,74,60), tolerance=5):
                                heart.click(1249,423)
                                time.sleep(0.5)
                          if heart.pixelMatchesColor(1155 , 773 ,(121,  51,  55), tolerance=5) :
                            print("cofre 1")
                            heart.press('5')
                            time.sleep(0.5)
                            heart.click(1040,515)
                            time.sleep(1)
                          """if heart.pixelMatchesColor(1155 , 773 ,(121,  51,  55), tolerance=5) and c and u:
                            print("cofre 2")
                            heart.press('5')
                            time.sleep(0.5)
                            heart.click(c + 36, u-18)
                            time.sleep(1)
                          if heart.pixelMatchesColor(1155 , 773 ,(121,  51,  55), tolerance=5) and c and u:
                            print("cofre 3")
                            heart.press('5')
                            time.sleep(0.5)
                            heart.click(c-35,0)
                            time.sleep(1)"""
                           
                          heart.moveTo(1272,754) 

                          if heart.pixelMatchesColor(1202,424, (81,74,60), tolerance=5):
                                heart.click(1249,423)
                                time.sleep(0.5)
                          time.sleep(.1)
                          heart.moveTo(1272,754)
                        
                            
                     heart.keyUp('shift')
                
                    except TypeError:
                    
                          pass
                        
                
                 time.sleep(0.5)
                 # mochila
                 if heart.pixelMatchesColor(1112,781, (255, 255, 255), tolerance=5) and modo == 'combate':
                    print("entra a mochila 1")
                    


                    

                  #  c,u = enemigo_mas_cercano_al_aliado("ali-n.png",
                  #                                          "ali-n.png")
                    print("semochilae")
                     #mochila
                    if heart.pixelMatchesColor(1112,781, (255, 255, 255), tolerance=5) :
                        
                        
                        if heart.pixelMatchesColor(1112,781, (255, 255, 255), tolerance=5) :
                            heart.press('4')
                            time.sleep(0.2)
                            heart.click(947,469)
                            time.sleep(1)
                        """if heart.pixelMatchesColor(1112,781, (255, 255, 255), tolerance=5) and c and u:
                            heart.press('4')
                            time.sleep(0.2)
                            heart.click(c-35, u+35)
                            time.sleep(1)                        if heart.pixelMatchesColor(1112,781, (255, 255, 255), tolerance=5) and c and u:
                            heart.press('4')
                            time.sleep(0.2)
                            heart.click(c+35, u+17)
                            time.sleep(1)
                            heart.moveTo(1272,754) """

                        if heart.pixelMatchesColor(1202,424, (81,74,60), tolerance=5):
                                heart.click(1249,423)
                                time.sleep(0.1)
                    
                        time.sleep(.1)
                        heart.moveTo(1272,754)        
                     
                 # suerte
                 if heart.pixelMatchesColor(1189 , 782, (255, 255, 255), tolerance=5) and modo == 'combate':
                    


                    try:


                     #suerte
                     while heart.pixelMatchesColor(1189 , 782, (255, 255, 255), tolerance=5) :
                          print("suerte")
                            
        
                          heart.moveTo(1190,782)
                          time.sleep(0.2)
                        
                          heart.click(button='right')
                        
                          time.sleep(0.5)
                          heart.moveTo(1272,754) 

                          if heart.pixelMatchesColor(1202,424, (81,74,60), tolerance=5):
                                    heart.click(1249,423)
                                    time.sleep(0.1)
                        
                                
                     heart.keyUp('shift')
                
                    except TypeError:
                    
                          pass
                 #pala masacrante  
                 if heart.pixelMatchesColor(1038, 774 ,(151, 168, 195), tolerance=5) and modo == 'combate' and heart.pixelMatchesColor(354, 212, (255,255,255), tolerance=5):
                    print("masacrante")
                    
                    
                    try:
                        try:
                            x,y = enemigo_mas_cercano_al_aliado2(jala, sadi, debug=True)
                            print(x,y)
                        except TypeError:

                            try:
                                x,y= (1226 , 663)
                                print(x,y)

                            except TypeError:
                                pass




                        #masacrante
                        if heart.pixelMatchesColor(1038, 774 ,(151, 168, 195), tolerance=5)   and not heart.pixelMatchesColor(1006, 776,(170, 135,  26), tolerance=5) and heart.pixelMatchesColor(354, 212, (255,255,255), tolerance=5) and modo == 'combate':
                            print("masacrante")



                            #
                            heart.press('2')
                            time.sleep(0.2)
                            heart.click(x,y)
                            time.sleep(.1)
                            heart.moveTo(1272,754)
                            if not heart.pixelMatchesColor(346,213, (255,255,255), tolerance=5):
                                break

                            if heart.pixelMatchesColor(1202,424, (81,74,60), tolerance=5):
                                        heart.click(1249,423)
                                        time.sleep(0.2)
                                        heart.moveTo(1007,778)
                                        time.sleep(0.2)

                                        heart.click(button='right')





                    except TypeError:


                            pass
                    time.sleep(3)

                 #pala masacrante
                 if heart.pixelMatchesColor(1038, 774 ,(151, 168, 195), tolerance=5) and modo == 'combate' and heart.pixelMatchesColor(354, 212, (255,255,255), tolerance=5):
                    print("masacrante")


                    try:
                        try:
                            x,y = enemigo_mas_lejano_al_aliado2(jala, sadi, debug=True)
                            print(x,y)
                        except TypeError:

                            try:
                                x,y= (1226 , 663)
                                print(x,y)

                            except TypeError:
                                pass


        
        
                        #masacrante
                        if heart.pixelMatchesColor(1038, 774 ,(151, 168, 195), tolerance=5)   and not heart.pixelMatchesColor(1006, 776,(170, 135,  26), tolerance=5) and heart.pixelMatchesColor(354, 212, (255,255,255), tolerance=5) and modo == 'combate':
                            print("masacrante")
                            
                            
                            
                            #
                            heart.press('2')
                            time.sleep(0.2)
                            heart.click(x,y)
                            time.sleep(.1)
                            heart.moveTo(1272,754)
                            if not heart.pixelMatchesColor(346,213, (255,255,255), tolerance=5):
                                break
        
                            if heart.pixelMatchesColor(1202,424, (81,74,60), tolerance=5):
                                        heart.click(1249,423)
                                                         
                            
                            
                            
                    except TypeError:
                        
                        
                            pass   
                    time.sleep(3)
                  
                 #juicio
                 time.sleep(1)
                 if heart.pixelMatchesColor(1074 , 779 ,( 47,  82, 136), tolerance=5) and modo == 'combate' and heart.pixelMatchesColor(354, 212, (255,255,255), tolerance=5):
                    
                    
                    try:
                        try:

                            x,y = enemigo_mas_cercano_al_aliado2(jala, sadi, debug=True)
                            print(x,y)
                        except TypeError:
                            pass
                            try:
                                x,y= (1226 , 663)
                                print(x,y)

                            except TypeError:
                                pass



                        #azo
                        if heart.pixelMatchesColor(1074 , 779 ,( 47,  82, 136), tolerance=5)  and not heart.pixelMatchesColor(1008,785,(190,185,152), tolerance=5) and heart.pixelMatchesColor(346,213, (255,255,255), tolerance=5) and modo == 'combate':
                            print("juicio")
                            
                            
                            
                            #azotadora
                            heart.press('3')
                            time.sleep(0.2)
                            heart.click(x,y)
                            time.sleep(.1)
                            
                            
                            heart.moveTo(1272,754)
                            if not heart.pixelMatchesColor(346,213, (255,255,255), tolerance=5):
                                break
        
                            if heart.pixelMatchesColor(1202,424, (81,74,60), tolerance=5):
                                        heart.click(1249,423)
                                        
                            
                            
                            
                    except TypeError:
                        
                        
                            pass
                    time.sleep(1)   
                 """zz"""    
                    #time.sleep(1.5)           
                #azotradora

                 print("termina turni y pasa")              
                 heart.press('space')
                 time.sleep(1) 
                 turno +=1
                 if turno >= 10: 
                    
                    winsound.PlaySound('sonido.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
             print("siquie aqui") 

        

        time.sleep(1)
        espera = 0   
        while True:
            print("entra la wile de cerrar ventans")
            time.sleep(.2)
            #espera += 1
            if espera == 10:
                print("entra aca -2")
                break
            recnec()   
            pelear3()   
            
            if heart.pixelMatchesColor(1262, 302, (255, 255, 255), tolerance=5) and heart.pixelMatchesColor(1262, 527 , (255, 255, 255), tolerance=5):
                time.sleep(1)
                
                
                pyautogui.press('esc')
                print("entra a cerrar")
                espera = 0 
                while True:
                    time.sleep(1)
                    if espera == 5:
                        break
                    pelear3()  
                    recnec()
                    if heart.pixelMatchesColor(1036, 810, (255, 255, 255), tolerance=5):
                        time.sleep(2)
                        if  heart.pixelMatchesColor(784 ,421 ,(255, 255, 255), tolerance=15) and heart.pixelMatchesColor(835, 540 ,(255,  97,   0), tolerance=15):
                            time.sleep(1)
                            heart.click(835, 540)
                        print("entra aca -1")
                        
                        time.sleep(1)
                        break
                if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):   
                    print("entra aca 1") 
                    mapa1() 
                    break
                break  
            time.sleep(2.5)
            if not heart.pixelMatchesColor(1262, 302, (255, 255, 255), tolerance=5) and not heart.pixelMatchesColor(1262, 527 , (255, 255, 255), tolerance=5):
                print("entra aca 2")
                modificarinventario()
                break  
            print("ya salio 1")
        print("ya salio 2")
        modificarinventario()
 
def vent_pelea():
    if heart.pixelMatchesColor(1262, 302, (255, 255, 255), tolerance=5) and heart.pixelMatchesColor(1262, 527 , (255, 255, 255), tolerance=5):
                time.sleep(1)
                
                ventana_nivel()
                pyautogui.press('esc')
                print("entra a cerrar")
                espera = 0 
                while True:
                    time.sleep(1)
                    if espera == 10:
                        break
                    recnec()
                    if heart.pixelMatchesColor(1036, 810, (255, 255, 255), tolerance=5):
                        heart.click(1044, 820, clicks=2,interval=.2)
                        time.sleep(.3)
                        heart.click(1112, 817, clicks=10,interval=.2)
                        break
                           
# ============================================================================
# ============================================================================
# SISTEMA DE PATHFINDING PARA DOFUS RETRO 1.47 - DETECCIÓN AUTOMÁTICA
# ============================================================================

class MapaDofusRetro:
    """
    Sistema de mapa para Dofus Retro con detección automática de celdas caminables
    """
    def __init__(self):
        # Región del mapa en la pantalla (AJUSTAR según tu resolución)
        self.region_mapa = (318, 132, 906, 580)  # (x, y, ancho, alto)
        
        # Mapa de celdas: None = no escaneado, True = caminable, False = bloqueado
        self.celdas = {}
        
    def es_color_caminable(self, color):
        """
        VERSIÓN MEJORADA: Detecta celdas grises medios/claros
        Rechaza grises oscuros que pueden ser transiciones a negro
        """
        r, g, b = color
        
        # Calcular propiedades del color
        diferencia_rgb = max(abs(r-g), abs(g-b), abs(r-b))
        promedio = (r + g + b) / 3
        minimo = min(r, g, b)
        maximo = max(r, g, b)
        
        # CRITERIO 1: Debe ser gris (componentes similares)
        if diferencia_rgb > 35:
            return False
        
        # CRITERIO 2: No debe ser muy oscuro (evitar grises-casi-negros)
        if promedio < 90:  # Más estricto que antes (era 80)
            return False
        
        # CRITERIO 3: No debe ser muy claro
        if promedio > 200:
            return False
        
        # CRITERIO 4: Todos los componentes RGB deben estar en rango medio
        if minimo < 70:  # Si algún componente es muy bajo, rechazar
            return False
        
        # CRITERIO 5: Verificar que es un gris uniforme
        rango = maximo - minimo
        if rango > 40:
            return False
        
        return True
    
    def es_color_negro_o_obstaculo(self, color):
        """
        Detecta específicamente celdas NEGRAS/oscuras (obstáculos)
        Retorna True si es obstáculo, False si NO es obstáculo
        """
        r, g, b = color
        promedio = (r + g + b) / 3
        
        # Método 1: Muy oscuro = Negro
        if promedio < 50:
            return True
        
        # Método 2: Oscuro con poca variación = Negro/Sombra profunda
        if promedio < 80:
            diferencia_rgb = max(abs(r-g), abs(g-b), abs(r-b))
            if diferencia_rgb < 20:  # Es gris muy oscuro = casi negro
                return True
        
        return False
    
    def escanear_mapa_actual(self):
        """
        Escanea el mapa visible en pantalla para detectar celdas caminables.
        Muestrea 5 puntos por celda (centro + 4 puntos interiores) y decide
        por mayoría, evitando falsos positivos por píxeles de borde.
        """
        print("🔍 Escaneando mapa...")

        screenshot = pyautogui.screenshot(region=self.region_mapa)
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        ancho_celda = 52
        alto_celda = 26
        h, w = screenshot_bgr.shape[:2]

        self.celdas = {}
        celdas_caminables = 0
        celdas_bloqueadas = 0

        for y_grid in range(0, h, alto_celda):
            for x_grid in range(0, w, ancho_celda):
                celda_id = (x_grid // ancho_celda, y_grid // alto_celda)

                # 5 puntos de muestreo: centro + interior de los 4 cuadrantes
                cx = x_grid + ancho_celda // 2
                cy = y_grid + alto_celda // 2
                qx = ancho_celda // 4
                qy = alto_celda // 4
                puntos = [
                    (cx,      cy     ),  # centro
                    (cx - qx, cy - qy),  # cuadrante superior-izq
                    (cx + qx, cy - qy),  # cuadrante superior-der
                    (cx - qx, cy + qy),  # cuadrante inferior-izq
                    (cx + qx, cy + qy),  # cuadrante inferior-der
                ]

                votos_caminable = 0
                votos_obstaculo = 0

                for px, py in puntos:
                    px = max(0, min(px, w - 1))
                    py = max(0, min(py, h - 1))
                    bgr = screenshot_bgr[py, px]
                    rgb = (int(bgr[2]), int(bgr[1]), int(bgr[0]))

                    if self.es_color_negro_o_obstaculo(rgb):
                        votos_obstaculo += 1
                    elif self.es_color_caminable(rgb):
                        votos_caminable += 1

                # Mayoría simple decide si la celda es caminable
                if votos_caminable > votos_obstaculo:
                    self.celdas[celda_id] = True
                    celdas_caminables += 1
                else:
                    self.celdas[celda_id] = False
                    celdas_bloqueadas += 1

        print(f"✅ Escaneo completo: {celdas_caminables} caminables, {celdas_bloqueadas} bloqueadas")

        # DEBUG: Descomentar para ver el mapa detectado
        # self.mostrar_mapa_debug()
        # self.guardar_mapa_debug_visual()

        return celdas_caminables > 0
    
    def es_caminable(self, celda):
        """Verifica si una celda es caminable"""
        if celda not in self.celdas:
            return False
        return self.celdas[celda]
    
    def obtener_vecinos(self, celda):
        """
        Obtiene celdas vecinas caminables según el sistema ISOMÉTRICO de Dofus Retro.
        Los 4 movimientos posibles son las 4 diagonales en el grid de pantalla,
        equivalentes a los 4 movimientos cardinales en la vista isométrica del juego.
        Solo se requiere que la celda destino sea caminable.
        """
        x, y = celda
        vecinos = []

        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            vecino = (x + dx, y + dy)
            if self.es_caminable(vecino):
                vecinos.append(vecino)

        return vecinos
    
    def pixel_a_celda(self, px, py):
        """Convierte coordenadas de píxel absoluto a celda del mapa"""
        x_rel = px - self.region_mapa[0]
        y_rel = py - self.region_mapa[1]
        
        ancho_celda = 52
        alto_celda = 26
        
        celda_x = x_rel // ancho_celda
        celda_y = y_rel // alto_celda
        
        return (int(celda_x), int(celda_y))
    
    def celda_a_pixel(self, celda):
        """Convierte celda a coordenadas de píxel (centro de la celda)"""
        x, y = celda
        
        ancho_celda = 52
        alto_celda = 26
        
        px = self.region_mapa[0] + (x * ancho_celda) + (ancho_celda // 2)
        py = self.region_mapa[1] + (y * alto_celda) + (alto_celda // 2)
        
        return (px, py)
    
    def mostrar_mapa_debug(self):
        """
        Muestra visualmente qué celdas detectó el sistema en modo ASCII
        """
        if not self.celdas:
            print("⚠️  No hay mapa escaneado")
            return
        
        print("\n" + "="*70)
        print("🗺️  MAPA DETECTADO (Vista ASCII)")
        print("="*70)
        print("█ = Celda CAMINABLE (gris detectado)")
        print("░ = Celda BLOQUEADA (negro/oscuro detectado)")
        print("="*70)
        
        if not self.celdas:
            return
        
        max_x = max(celda[0] for celda in self.celdas.keys())
        max_y = max(celda[1] for celda in self.celdas.keys())
        
        for y in range(max_y + 1):
            linea = f"{y:2d} │ "
            for x in range(max_x + 1):
                if (x, y) in self.celdas and self.celdas[(x, y)]:
                    linea += "█ "
                else:
                    linea += "░ "
            print(linea)
        
        print("   └" + "─"*(max_x*2+1))
        print("     " + " ".join([f"{x}" for x in range(max_x + 1)]))
        print("="*70)
        print(f"Total celdas caminables: {sum(1 for v in self.celdas.values() if v)}")
        print(f"Total celdas bloqueadas: {sum(1 for v in self.celdas.values() if not v)}")
        print("="*70 + "\n")
    
    def guardar_mapa_debug_visual(self):
        """
        Guarda imagen mostrando qué detectó: Verde=caminable, Rojo=bloqueado
        """
        print("💾 Guardando imagen de debug del mapa...")
        
        screenshot = pyautogui.screenshot(region=self.region_mapa)
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        ancho_celda = 52
        alto_celda = 26
        
        # Dibujar overlay sobre el screenshot
        for celda, es_caminable in self.celdas.items():
            x_grid, y_grid = celda
            
            x_px = x_grid * ancho_celda
            y_px = y_grid * alto_celda
            
            if es_caminable:
                color_overlay = (0, 255, 0)  # Verde = caminable
                alpha = 0.3
            else:
                color_overlay = (0, 0, 255)  # Rojo = bloqueado
                alpha = 0.5
            
            overlay = screenshot_bgr.copy()
            cv2.rectangle(overlay, 
                         (x_px, y_px), 
                         (x_px + ancho_celda, y_px + alto_celda), 
                         color_overlay, 
                         -1)
            
            screenshot_bgr = cv2.addWeighted(overlay, alpha, screenshot_bgr, 1 - alpha, 0)
        
        cv2.imwrite('mapa_detectado.png', screenshot_bgr)
        print("✅ Imagen guardada: mapa_detectado.png")
        print("   💚 Verde = Celdas caminables")
        print("   🔴 Rojo = Celdas bloqueadas")

def heuristica_dofus(a, b):
    """
    Distancia Chebyshev para pathfinding isométrico de Dofus.
    Con movimientos solo en (±1,±1), la distancia mínima real entre dos celdas
    es max(|dx|, |dy|). Manhattan sobreestima y arruina las prioridades de A*.
    """
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def a_star_dofus(mapa, inicio, objetivo, pm_disponibles=4):
    """Algoritmo A* adaptado para Dofus Retro con límite de PM"""
    if inicio == objetivo:
        return [inicio]
    
    frontera = []
    heapq.heappush(frontera, (0, inicio))
    
    vino_de = {inicio: None}
    costo_hasta = {inicio: 0}
    
    while frontera:
        _, actual = heapq.heappop(frontera)
        
        if actual == objetivo:
            camino = []
            while actual:
                camino.append(actual)
                actual = vino_de[actual]
            camino = camino[::-1]
            
            if len(camino) - 1 <= pm_disponibles:
                return camino
            else:
                return camino[:pm_disponibles + 1]
        
        if costo_hasta[actual] >= pm_disponibles:
            continue
        
        for vecino in mapa.obtener_vecinos(actual):
            nuevo_costo = costo_hasta[actual] + 1
            
            if nuevo_costo <= pm_disponibles:
                if vecino not in costo_hasta or nuevo_costo < costo_hasta[vecino]:
                    costo_hasta[vecino] = nuevo_costo
                    prioridad = nuevo_costo + heuristica_dofus(vecino, objetivo)
                    heapq.heappush(frontera, (prioridad, vecino))
                    vino_de[vecino] = actual
    
    # Camino parcial si no puede llegar
    if not vino_de or len(vino_de) <= 1:
        return [inicio]
    
    mejor_celda = inicio
    mejor_distancia = heuristica_dofus(inicio, objetivo)
    
    for celda in vino_de.keys():
        if celda != inicio:
            dist = heuristica_dofus(celda, objetivo)
            if dist < mejor_distancia:
                mejor_distancia = dist
                mejor_celda = celda
    
    camino = []
    actual = mejor_celda
    while actual and len(camino) <= pm_disponibles:
        camino.append(actual)
        actual = vino_de.get(actual)
    
    return camino[::-1] if camino else [inicio]

def ejecutar_movimiento_dofus(camino, mapa):
    """Ejecuta el movimiento en Dofus haciendo click en las celdas"""
    if not camino or len(camino) <= 1:
        print("⚠️  No hay movimiento que ejecutar")
        return
    
    print(f"🎮 Ejecutando movimiento: {len(camino)-1} PM")
    
    for i, celda in enumerate(camino[1:], 1):
        px, py = mapa.celda_a_pixel(celda)
        print(f"  Paso {i}: Celda {celda} -> Píxel ({px}, {py})")
        
        heart.click(px, py,interval=.3)
        time.sleep(0.4)
    
    print(f"✅ Movimiento completado: {len(camino)-1} PM gastados")

def caminar_dofus_inteligente(mapa, pm_disponibles=4):
    """
    Sistema de movimiento inteligente para Dofus Retro
    Reemplaza a caminar2() con detección automática de celdas
    """
    try:
        # Buscar posiciones
        x1, y1 = buscar_imagen_en_pantalla2(sadi)
        x2, y2 = buscar_imagen_en_pantalla2(jala)
        
        print(f"\n🎯 Aliado en píxel: ({x1}, {y1})")
        print(f"🎯 Enemigo en píxel: ({x2}, {y2})")
        
        # Convertir a celdas
        celda_aliado = mapa.pixel_a_celda(x1, y1)
        celda_enemigo = mapa.pixel_a_celda(x2, y2)
        
        print(f"📍 Aliado en celda: {celda_aliado}")
        print(f"📍 Enemigo en celda: {celda_enemigo}")
        
        # Verificar distancia
        distancia_pixels = calcular_distancia((x1, y1), (x2, y2))
        print(f"📏 Distancia en píxeles: {distancia_pixels:.1f}")
        
        # Solo moverse si está lejos y en turno de movimiento
        if distancia_pixels < 250:
            print("✋ Demasiado cerca del enemigo")
            return False
        
        if not heart.pixelMatchesColor(345, 215, (255, 255, 255)):
            print("⏸️  No es turno de movimiento")
            return False
        
        # Escanear mapa en cada llamada: cada combate puede ser en una sala diferente
        mapa.escanear_mapa_actual()
        
        # Buscar camino
        print(f"🔍 Buscando camino óptimo (máx {pm_disponibles} PM)...")
        camino = a_star_dofus(mapa, celda_aliado, celda_enemigo, pm_disponibles)
        
        if not camino or len(camino) <= 1:
            print("❌ No se encontró camino válido")
            return False
        
        print(f"✅ Camino encontrado: {camino}")
        print(f"📊 Longitud: {len(camino)-1} celdas")
        
        # Ejecutar movimiento
        ejecutar_movimiento_dofus(camino, mapa)
        
        # Limpiar cursor
        heart.moveTo(1272, 754)
        time.sleep(0.3)
        
        # Verificar diálogos
        if (heart.pixelMatchesColor(1097, 246, (81, 74, 60), tolerance=5) or 
            heart.pixelMatchesColor(1141, 228, (81, 74, 60), tolerance=5) or  
            heart.pixelMatchesColor(1095, 218, (81, 74, 60), tolerance=5) or 
            heart.pixelMatchesColor(993, 175, (213, 207, 170), tolerance=5)):
            heart.press("esc")
        
        return True
        
    except TypeError as e:
        print(f"❌ Error al buscar imágenes: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en movimiento: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# FIN DEL SISTEMA DE PATHFINDING PARA DOFUS RETRO
# ============================================================================

# ============================================================================

def caminar2(umbral,umbral2):

    distancia=260
    sx2, sy2 = 841, 421
    dx,dy = 900,600

    try :
       
       x1,y1= buscar_imagen_en_pantalla2(sadi)
       print(f"posicion de aliado es {x1,y1}")
       

       
       x2,y2= buscar_imagen_en_pantalla2(jala)
       print(f"posicion de aliado es {x2,y2}")
       
       #calcula la distancia entre los dos puntos
       distancia = calcular_distancia((x1, y1), (x2, y2))
       
       sx2,sy2 = x2,y2
       
    
    except TypeError:
        
       try: 
          
          x1,y1 = buscar_imagen_en_pantalla2(sadi) #heart.locateCenterOnScreen("sadi2.png", confidence= 0.525, region=(310,132,964,580))
          x2,y2 = buscar_imagen_en_pantalla2(jala )#heart.locateCenterOnScreen('jalato2.png', confidence= 0.525, region=(310,132,964,580))

          #calcula la distancia entre los dos puntos
          distancia = calcular_distancia((x1, y1), (x2, y2))

          
          sx2,sy2 = x2,y2
       
       except TypeError:
          
          print('no se encontrò alguno de los dos')
       
          x2,y2 = sx2,sy2
          #pelear()

    try:
        dx = x2 - x1 
        dy = y2 - y1

    except UnboundLocalError:
        pass
    
    time.sleep(.5)
        
    if distancia >= 250 and heart.pixelMatchesColor(345 ,215 , (255, 255, 255)):
       print("entra al promer if")
       if abs(dx) <= umbral:
           print("entra al 2 if")
           if dy > 0:
               print("2222#Abajo izquierda")
               heart.click(x1-33,y1+54) 
               time.sleep(.2)
               heart.click(x1+33,y1+51) #Abajo
               time.sleep(.2)
               heart.click(x1+101,y1+51)
               time.sleep(.2)
           else:
               print("22222#Arrib izquierdaa")
               heart.click(x1-35,y1-51) 
               time.sleep(.2)
               heart.click(x1+34,y1-51) #Arriba
               time.sleep(.2)
               heart.click(x1+98,y1-43)
               time.sleep(.2)
       elif abs(dy) <= umbral:
           if dx > 0:
               print("2222#Derecha arriba")
               heart.click(x1+95,y1-16) 
               time.sleep(.2)
               heart.click(x1+91,y1+20) 
               time.sleep(.2)
               heart.click(x1+101,y1+51)
               time.sleep(.2) #Derecha"
           else:
               print("222222#Izquierda arriba")
               heart.click(x1-100,y1-18) 
               time.sleep(.2)
               heart.click(x1-100,y1+18) 
               time.sleep(.2)
               heart.click(x1-102,y1+54)
               time.sleep(.2) #Izquierda"
       elif dx > 0 and dy > 0:
           print("Abajo a la derecha")
           heart.click(x1+100,y1+52,clicks=2, interval=0.3)
            
           time.sleep(.2)
           heart.click(x1+32,y1+56,clicks=2, interval=0.3)

           time.sleep(.2)
           heart.click(x1+102,y1+19,clicks=2, interval=0.3)
           time.sleep(.2)           
           #time.sleep(.5)#Abajo a la derecha"
           heart.click(x1+103,y1-148,clicks=2, interval=0.3) 
       
       elif dx > 0 and dy < 0:
           
           print("Arriba a la derecha")
           heart.click(x1+98,y1-50,clicks=2, interval=0.3) 
           time.sleep(.2)
           heart.click(x1+95,y1-16,clicks=2, interval=0.3) 
           time.sleep(.2)
           heart.click(x1+33,y1-53,clicks=2, interval=0.3) 
           time.sleep(.2)
           heart.click(x1-100,y1-53,clicks=2, interval=0.3)
           #time.sleep(.2)
           #heart.click(x1+103,y1+51) 
           
           #time.sleep(.5)#Arriba a la derecha"
       

       elif dx < 0 and dy > 0:
           print("Abajo a la izquierda")
           heart.click(x1-103,y1+51,clicks=2, interval=0.3)
           
           time.sleep(.2)           
           #Abajo a la derecha"
           heart.click(x1-27,y1+51,clicks=2, interval=0.3) 
           time.sleep(.2)
           heart.click(x1-100,y1+19,clicks=2, interval=0.3) 
           time.sleep(.2)
           heart.click(x1-100,y1-53,clicks=2, interval=0.3)
           #heart.click(x1+100,y1+56,clicks=2, interval=0.3)
           
           
         
       elif dx < 0 and dy < 0:
           print("Arriba a la izquierda")
                     
           #time.sleep(.5)#Arriba a la derecha"
           heart.click(x1-100,y1-52,clicks=2, interval=0.3) 
           time.sleep(.2)
           heart.click(x1-100,y1-17,clicks=2, interval=0.3) 
           time.sleep(.2)
           heart.click(x1-35,y1-54,clicks=2, interval=0.3)
           time.sleep(.2)
           heart.click(x1-103,y1+51,clicks=2, interval=0.3)
           #heart.click(x1,y1+49)

           
       if heart.pixelMatchesColor(1097 ,246 ,( 81,  74,  60), tolerance=5) or heart.pixelMatchesColor(1141 ,  228 ,( 81,  74,  60), tolerance=5)  or heart.pixelMatchesColor(1095 , 218 ,( 81,  74,  60), tolerance=5) or heart.pixelMatchesColor(993, 175 , (213, 207, 170), tolerance=5):
            heart.press("esc")
       heart.moveTo(1272,754)
       time.sleep(0.5)

  
def mapa1():
    while True:    
        recnec()
        if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):     
            
            
            heart.click (1269,402)
            contador = 0
            while True:
                time.sleep(.2)
                contador = contador + 1
                if contador == 50:
                    break
                recnec()
                if heart.pixelMatchesColor(946, 155, (225, 219, 198), tolerance=10): 

                    break
        
        

        if heart.pixelMatchesColor(946, 155, (225, 219, 198), tolerance=10):      
            
            
            heart.click (842,157)
            contador = 0    
            while True:
                contador = contador + 1
                if contador == 50:
                    break
                recnec()
                if heart.pixelMatchesColor(782, 669, (224, 222, 198), tolerance=10):      
                    break
    
    
        if heart.pixelMatchesColor(782, 669, (224, 222, 198), tolerance=10):
            
            heart.click (1247,438)
        
            contador = 0    
            while True:
                contador = contador + 1
                if contador == 50:
                    break
                recnec()
                if heart.pixelMatchesColor(576, 314, (247, 188,  58), tolerance=10):    
                    break

        if  heart.pixelMatchesColor(576, 314, (247, 188,  58), tolerance=10):
        
        
            
            heart.click (1109,158)
        
            contador = 0    
            while True:
                contador = contador + 1
                if contador == 100:
                    break
                recnec()
                if heart.pixelMatchesColor(1022,  580, (225, 221, 203), tolerance=10):     
                    break
    
    
        if  heart.pixelMatchesColor(1022,  580, (225, 221, 203), tolerance=10): 
        
            
            
            heart.click (974,162)
            
            contador = 0    
            while True:
                contador = contador + 1
                if contador == 50:
                    break
                recnec()
                if heart.pixelMatchesColor(915, 329, (222, 223, 197), tolerance=10):  
                    break
    
    
        if heart.pixelMatchesColor(915, 329, (222, 223, 197), tolerance=10):         
            
            heart.click (771,220)
            
            contador = 0    
            while True:
                contador = contador + 1
                if contador == 50:
                    break
                recnec()
                print("se queda contando")
                time.sleep(1)
                contador += 1
                if heart.pixelMatchesColor(1130,  346, (144, 110,  57), tolerance=10):  
                    print("sale de mapa")   
                    break
            break
        
   # return

def rutas():
    if not heart.locateCenterOnScreen(os.path.join(_DIR, 'recorrido1.png'), confidence=0.55, region=(806,732,116,105)) and ruta ==1:
        print("ejecuta la ruta")
        mapa1()
        
        

def caminarMina():
    registrar_progreso()
    recnec()
    ventana_nivel()
    if not heart.pixelMatchesColor(946, 155, (225, 219, 198), tolerance=10) or not heart.pixelMatchesColor(672, 450, ( 92,  86,  64), tolerance=10) or not heart.pixelMatchesColor(497, 426, (153, 135, 108), tolerance=10):
        print("no se detecta sala 1")
        
    
        print("arranca del zap")
        pelear2()
        heart.moveTo(1007, 783)
        time.sleep(.3)
        heart.click(clicks=2, interval=.03)     
        time.sleep(3)
        
    while True:
        recnec()
        if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
            
            mapa1()
            break
            
    return
    #else:
        #pelear()    
            
            
    
       

def ventana_nivel():
    
    if heart.pixelMatchesColor(1018 , 366 , (255, 255, 255), tolerance=20):
        time.sleep(.5)
        heart.moveTo(828, 454)
        time.sleep(.5)
        heart.click()
        time.sleep(3)
    
    

def ir_banco():
    registrar_progreso()
    # Si está en sala de mineros → no ir al banco, seguir minando
    if heart.pixelMatchesColor(809, 416, (92, 86, 66), tolerance=10) and heart.pixelMatchesColor(885, 288, (147, 109, 45), tolerance=10):
        print("ir_banco: sala de mineros detectada — cancelando, continúa minando")
        return
    print("usa posima bonta")
    time.sleep(.5)
    heart.moveTo(1007,818)
    time.sleep(.5)
    heart.click(clicks=2, interval=.05)
    time.sleep(1)

    # Espera hasta 10s para detectar milicia (bonta); si no aparece, reusa poción
    inicio_espera = time.time()
    while True:
        recnec()
        if heart.pixelMatchesColor(1246, 661, (77, 77, 38), tolerance=15) and heart.pixelMatchesColor(524, 230, (119, 128, 50), tolerance=15):
            break
        if time.time() - inicio_espera > 10:
            print("no detectó bonta en 10s — reintentando poción")
            heart.moveTo(1007, 818)
            time.sleep(.5)
            heart.click(clicks=2, interval=.05)
            time.sleep(1)
            inicio_espera = time.time()
        time.sleep(.2)

    romp = 0
    while True:
        time.sleep(.1)
        romp = romp + 1
        if romp > 200 :
            break
        recnec()

        while heart.pixelMatchesColor(1246,  661, ( 77,  77,  38), tolerance=15) and heart.pixelMatchesColor(524,  230, (119, 128,  50), tolerance=15):
            print("detecta milicia")
            
            cuenta = 0 
            while True:
                recnec()
                cuenta = cuenta + 1
                if cuenta == 10:
                    break
                time.sleep(1)
                print("esperando que camine al zapi")
                while True:    
                    if heart.pixelMatchesColor(1127, 184 ,(215, 186, 121), tolerance=15) and heart.pixelMatchesColor(1266,298 ,(207, 189, 133), tolerance=15):
                        time.sleep(.5)
                        heart.moveTo(1007,818)
                        time.sleep(.5)
                        heart.click(clicks=2, interval=.05)
                        time.sleep(1)

                    print("inicia zapi")    
                    recnec()
                    if heart.pixelMatchesColor(900 ,  190 , (255, 255, 255), tolerance=15) and heart.pixelMatchesColor(559 , 402 , (255, 255, 255), tolerance=15):
                        print("detecto ventana zapi y cierra")
                        
                        break
                    time.sleep(.5)
                    heart.click(815, 425)                                 
                    time.sleep(.5)           
                        
                    heart.click(873 ,464)
                    time.sleep(.5)
                    heart.click(968, 782 )
                    time.sleep(3)

                while True:
                    print("esperando que aparecio la ventana")
                    print
                    recnec()
                    if heart.pixelMatchesColor(900 ,  190 , (255, 255, 255), tolerance=15) and heart.pixelMatchesColor(559 , 402 , (255, 255, 255), tolerance=15):
                        break
                break
            cuenta = 0                
            while True:    
                print("esperando ventana zapi para dar clic a banco")
                recnec()
                time.sleep(0.2)
                cuenta = cuenta + 1
                if cuenta == 50:
                    break
                if heart.pixelMatchesColor(900 ,  190 , (255, 255, 255), tolerance=15) and heart.pixelMatchesColor(559 , 402 , (255, 255, 255), tolerance=15):
                    print("ventana")
                    time.sleep(.3)
                    heart.moveTo(652, 243)   
                    time.sleep(.2)      
                    heart.click()   
                    time.sleep(.3)  
                    heart.moveTo(648, 329)
                    time.sleep(.2)   
                      
                    heart.click()
                    time.sleep(2)     
                if heart.pixelMatchesColor(798,  297, (131, 124,  75), tolerance=15) and heart.pixelMatchesColor(1005, 342,  (133, 123,  90), tolerance=15):  
                    break    
            break           
        #ventana transporte
        
        #mapa banco
        
        while heart.pixelMatchesColor(798,  297, (131, 124,  75), tolerance=15) and heart.pixelMatchesColor(1005, 342,  (133, 123,  90), tolerance=15):
            
            
            
            print("detecta mapa banco")
            time.sleep(.3)
            heart.moveTo(850, 339)   
            time.sleep(.2)      
            heart.click()
            heart.click(968, 782 )
            cuenta = 0
            while True:
                recnec()
                time.sleep(0.2)
                cuenta = cuenta + 1
                if cuenta == 50:
                    break
                if heart.pixelMatchesColor(1065,  288 , (170, 158, 132), tolerance=15) and heart.pixelMatchesColor(780,  163,  (130, 129,  34), tolerance=15):
                    break       
            break        
              
        while heart.pixelMatchesColor(1065,  288 , (170, 158, 132), tolerance=15) and heart.pixelMatchesColor(780,  163,  (130, 129,  34), tolerance=15):            
            
                
            while True:   
                recnec()
                print("hablar con buho")
                if heart.pixelMatchesColor(478 ,230 ,(182, 147,  31), tolerance=15): 
                    break
                print("sique hablacno")
                #moverr buho
                time.sleep(1)
                heart.moveTo(946,  302)   
                time.sleep(.4)      
                heart.click()
                #hablar buho
                time.sleep(.3)
                heart.moveTo(994, 318)   
                time.sleep(.4)      
                heart.click()

                time.sleep(3)

            cuenta = 0  
            while True:
                recnec()
                time.sleep(0.2)
                cuenta = cuenta + 1
                if cuenta == 300:
                    break
                if heart.pixelMatchesColor(602, 337 , (255, 255, 206), tolerance=15):         
                      
                    time.sleep(.2)      
                    heart.click(666, 453)
                    time.sleep(.2) 

                if heart.pixelMatchesColor(1142, 262 , ( 81,  74,  60), tolerance=15):   
                    #clic recursos
                    time.sleep(1.5)
                    heart.click(425, 300)   
                    time.sleep(.2)
                    heart.moveTo(1102, 304)   
                    time.sleep(.2)      
                    heart.click()
                    #mover mineral
                    time.sleep(3)
                    heart.moveTo(1045, 371)   
                    #pasar mineral
                    while not heart.pixelMatchesColor(1056, 369,  (190, 185, 152), tolerance=15) or not heart.pixelMatchesColor(1053 ,357 , (190, 185, 152), tolerance=15) or not heart.pixelMatchesColor(1054, 377,(190, 185, 152), tolerance=15):
                        time.sleep(.4)      
                        heart.keyDown("ctrl")
                        heart.click(clicks=2, interval=0.1)
                        heart.keyUp(("ctrl"))

                    time.sleep(.3)
                    heart.click(507, 333)
                    time.sleep(.3)
                    #posicion = buscar_imagen_en_inventario("carne.png")
                    """print(posicion)
                    if posicion:
                        time.sleep(.3)
                        # Mover el cursor y hacer clic
                        pyautogui.moveTo(posicion[0], posicion[1], duration=0.1)
                        pyautogui.click()
                        heart.click(posicion[0], posicion[1], duration=0.1)
                        heart.moveTo(373, 364)
                        heart.mouseDown()
                        time.sleep(.2)
                        heart.moveTo(1136 ,486)
                        heart.mouseUp()
                        time.sleep(.2)
                        heart.write("10")
                        time.sleep(.4)
                        heart.press("enter")
                        time.sleep(.3)
                        heart.click(439,332)
                        time.sleep(.3)
                        heart.click(417,355)"""
                    #panes
                    if not heart.pixelMatchesColor(1115,822 , (129,  78,  45), tolerance=5): 
                        time.sleep(.3)
                        heart.click( 395 , 297)
                        time.sleep(2)

                        posicion = buscar_imagen_en_inventario("pan.png")
                        print(posicion)
                        if posicion:
                            # Mover el cursor y hacer clic
                            pyautogui.moveTo(posicion[0], posicion[1], duration=0.1)
                            pyautogui.click()
                            heart.moveTo(posicion[0], posicion[1], duration=0.1)
                            
                            heart.mouseDown()
                            time.sleep(.2)
                            heart.moveTo(1136 ,486)
                            heart.mouseUp()
                            time.sleep(.2)
                            heart.write("200")
                            time.sleep(.4)
                            heart.press("enter")
                    #pos bonta
                    if heart.pixelMatchesColor(1008,807, ( 61,  82, 108), tolerance=15): 
                        time.sleep(.3)
                        heart.click( 395 , 297)
                        time.sleep(2)

                        posicion = buscar_imagen_en_inventario("posimabonta.png")
                        print(posicion)
                        if posicion:
                            # Mover el cursor y hacer clic
                            pyautogui.moveTo(posicion[0], posicion[1], duration=0.1)
                            pyautogui.click()
                            heart.moveTo(posicion[0], posicion[1], duration=0.1)
                            
                            heart.mouseDown()
                            time.sleep(.2)
                            heart.moveTo(1136 ,486)
                            heart.mouseUp()
                            time.sleep(.2)
                            heart.write("200")
                            time.sleep(.4)
                            heart.press("enter")  
                    #p´os recuerdo    
                    if heart.pixelMatchesColor(1008,772, ( 76,  98,  89), tolerance=15): 
                        time.sleep(.3)
                        heart.click( 395 , 297)
                        time.sleep(2)

                        posicion = buscar_imagen_en_inventario("posimarecuerdo.png")
                        print(posicion)
                        if posicion:
                            # Mover el cursor y hacer clic
                            pyautogui.moveTo(posicion[0], posicion[1], duration=0.1)
                            pyautogui.click()
                            heart.moveTo(posicion[0], posicion[1], duration=0.1)
                            
                            heart.mouseDown()
                            time.sleep(.2)
                            heart.moveTo(1136 ,486)
                            heart.mouseUp()
                            time.sleep(2)
                            heart.write("200",interval=.5)
                            time.sleep(.4)
                            heart.press("enter")      
                    time.sleep(.3)
                    heart.moveTo(1249, 266)   
                    time.sleep(.3)  
                    heart.click()

                    #alimentar dragopavo

                    time.sleep(.5)
                    heart.click(1031, 718)
                    time.sleep(.3)
                    heart.click(1158, 252)
                    time.sleep(.3)
                    heart.moveTo(1090,346)
                    heart.mouseDown()
                    time.sleep(.3)
                    heart.moveTo(1010,404)
                    heart.mouseUp()
                    time.sleep(.3)
                    #heart.click(861,386,clicks=2,interval=.3)
                    time.sleep(.3)
                    heart.click(1247, 182)
                    time.sleep(.3)
                    break   
            break   
        """if not heart.pixelMatchesColor(827, 731, (255, 102,   0), tolerance=15) : 
            break """
        if  heart.pixelMatchesColor(578,264,(127, 126,  33), tolerance=15) : 
            break
    time.sleep(2)    
    heart.click(1252, 818,clicks=2,interval=.2)
    #usar posima de puelo    
    print("termina de pasar las cosas")   
    ir_mercado()     
    time.sleep(2)   
    heart.click(1040, 818,clicks=2,interval=.2) 
    return

def inventario():
    registrar_progreso()
    # Si está en pelea, intentar resolverla con pelear2 antes de seguir
    if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10) or heart.pixelMatchesColor(1264, 622, (255, 33, 33), tolerance=10):
        print("inventario: en pelea, llamando a pelear2")
        pelear2()
        return

    sala()
    if heart.pixelMatchesColor( 888 , 722 , (255, 175,   0), tolerance=5) :
        print("set minero")      
        heart.click(1044 ,  818,clicks=2,interval=.2)    
    print("revisa inventario")
    if heart.pixelMatchesColor(827, 731, (255, 102,   0), tolerance=15):
        """or not heart.pixelMatchesColor(1115,822 , (129,  78,  45), tolerance=5)"""
        print("inventario lleno")
        recnec()
        ir_banco()
        return caminarMina()
        
    print("inventario con espacio")
    
    return

def recolectar(x,y):
    registrar_progreso()
    heart.moveTo(x,y)
    time.sleep(.1)
    heart.click()
    heart.moveTo(x + 5, y + 40)
    time.sleep(.1)                 
       
    heart.click()     
       
      
#minabrak de aqui para abajo

def mapab1():
    #possim brak
    """time.sleep(0.8)
    heart.moveTo(1222,819)
    time.sleep(0.8)
    heart.click(clicks=2, interval=.05)"""
    #espero que renderice milicia
    while True:
        if heart.pixelMatchesColor(1126, 311, (104, 110,  94), tolerance=3) :
            print("detecta milicia")
            print("inicia zapi")    
            
            time.sleep(.2)
            heart.moveTo(1056, 243)   
            time.sleep(.2)      
            heart.click()   
            time.sleep(.3)  
            heart.moveTo(1149, 283)
            time.sleep(.2)      
            heart.click()
            break
    while True:
        if heart.pixelMatchesColor(934,  210, ( 81,  74,  60), tolerance=15) or heart.pixelMatchesColor(912, 616,  (147, 134, 108), tolerance=15):
            print("ventana zappi")
            #varios
            time.sleep(.3)
            heart.moveTo(734,  244)   
            time.sleep(.2)      
            heart.click()  
            #plaza mercante
            time.sleep(.3)  
            heart.moveTo(741, 460)
            time.sleep(.2)      
            heart.click()
            break

    while True:
        if heart.pixelMatchesColor(1249, 217, ( 58,  51,  28), tolerance=15) or heart.pixelMatchesColor(510, 429,  (250, 240, 192), tolerance=15):
            print("pa+laza mercante")
            time.sleep(.3)
            heart.moveTo(902, 150)   
            time.sleep(.2)      
            heart.click()            
            break

        
    contador = 0
    while True:
        
                     
        if heart.pixelMatchesColor(985,  255, (186, 181, 144), tolerance=3) or heart.pixelMatchesColor(1115, 156, (141, 132,  94), tolerance=3):     
             break
        contador = contador + 1
    
    #-26,31  -> -25,30  
    
    print("mapa 2")    
    time.sleep(0.8)
    heart.moveTo(1266, 233)
    heart.click ()
    contador = 0    
    while True:
        print("mapa en el wile")
        time.sleep(1)
        
        if heart.pixelMatchesColor(955, 384,( 66,  63,  47), tolerance=20) or  heart.pixelMatchesColor(1144, 307, (188, 143,  80), tolerance=20):   
             print("rompe wile")  
             break
  
    #-25,30   -> -25,29
    print("mapa 3")    
    time.sleep(0.8)
    heart.moveTo(1132, 159)
    heart.click ()
    contador = 0    
    while True:
        time.sleep(1)
       
        if heart.pixelMatchesColor(641, 209, (244, 241, 183), tolerance=20) or  heart.pixelMatchesColor(420, 600, (164, 115,  51), tolerance=20):     
             break
   
    #-26,29   ->-25,28
        
    time.sleep(0.8)
    heart.moveTo(930, 161)
    heart.click ()
    contador = 0    
    while True:
        time.sleep(1)
   
        if heart.pixelMatchesColor(554,  304, ( 97,  65,  51), tolerance=10) or  heart.pixelMatchesColor(1241, 214, ( 59,  52,  29), tolerance=10):     
             break

    #-26,28   
        
    time.sleep(0.8)
    heart.moveTo(930, 161)
    heart.click ()
    contador = 0    
    while True:
        time.sleep(1)
    
        if heart.pixelMatchesColor(1051, 516, ( 98,  64,  40), tolerance=10) or  heart.pixelMatchesColor(725, 252, (96,  65,  51), tolerance=10):     
             break
    
    #-26,27  
        
    time.sleep(0.8)
    heart.moveTo(930, 161)
    heart.click ()
    contador = 0    
    while True:
        time.sleep(1)
      
        if heart.pixelMatchesColor(691, 239, (99,  66,  51), tolerance=10) or  heart.pixelMatchesColor(1049, 449, (250, 240, 192), tolerance=10):     
             break
  
    #-26,26  
        
    time.sleep(0.8)
    heart.moveTo(795, 163)
    heart.click ()
    contador = 0    
    while True:
        time.sleep(1)
     
        if heart.pixelMatchesColor(1244, 261, ( 67,  54,  32), tolerance=10) or  heart.pixelMatchesColor(341, 558, ( 84,  54,  40), tolerance=10):     
             break

    #-25,24 _> mina  
        
    time.sleep(0.8)
    heart.moveTo(795, 163)
    heart.click ()
    contador = 0    
    while True:
        time.sleep(1)
       
        if heart.pixelMatchesColor(736, 315, (135, 132, 119), tolerance=10) or  heart.pixelMatchesColor(461, 577, (63,  53,  28), tolerance=10):     
             break
        contador += 1
   
    #-25,24 _> mina  
        
    time.sleep(0.8)
    heart.moveTo(659, 405)
    heart.click ()
    contador = 0    
    while True:
        time.sleep(1)
    
        if heart.pixelMatchesColor(910, 355 , (166, 119,  55), tolerance=10) or  heart.pixelMatchesColor(436, 154, ( 87,  63,  24), tolerance=10):     
            time.sleep(0.8)
            heart.moveTo(1126, 511)
            heart.click ()   
            contador += 1
            break
       
    while True:
        if heart.pixelMatchesColor(698,  495 , (153, 135, 108), tolerance=10) or  heart.pixelMatchesColor(614, 507, ( 93,  84,  64), tolerance=10): 
            time.sleep(0.8)
            heart.moveTo(346, 197)
            heart.click ()
            break     
    while True:
        if heart.pixelMatchesColor(344, 244 , (176, 144,  82), tolerance=10) or  heart.pixelMatchesColor(533, 161, (107, 106,  96), tolerance=10): 
            time.sleep(0.8)
            heart.moveTo(346, 197)
            heart.click ()
            break  
    while True:
        if heart.pixelMatchesColor(1126, 457 , (203, 158,  30), tolerance=10) or  heart.pixelMatchesColor(894, 424, (192, 182, 150), tolerance=10): 
            
            break 

def caminarMinab():
    registrar_progreso()
    while True:
        ventana_nivel()
        if heart.pixelMatchesColor(1126, 457 , (203, 158,  30), tolerance=3) or  heart.pixelMatchesColor(894, 424, (192, 182, 150), tolerance=3):
            print("se detecta sala 1")
            break
        else:
            print("arranca pa brak")
            
            heart.moveTo(1233, 822)
            time.sleep(.3)
            heart.click(clicks=2, interval=.03)     
            time.sleep(5)
            
            if heart.pixelMatchesColor(1158,326, ( 31,  38,  24), tolerance=10) or heart.pixelMatchesColor(946,  163, ( 73,  63,  32), tolerance=10):
                mapab1()
                
             
                
            print(" termina caminar")
        time.sleep(2)

def any_desk():
    if heart.pixelMatchesColor(326, 700 , ( 46, 151,  62), tolerance=5) and heart.pixelMatchesColor(477, 698 , (251,  65,  55), tolerance=5) and heart.pixelMatchesColor( 736 ,  278 , ( 95, 136, 207), tolerance=5):
        time.sleep(.3)
        heart.click(736,278,clicks=2,interval=.1)
        time.sleep(.3)
        heart.click(872, 247,clicks=2,interval=.1)

def minar_original(posiciones):
    print("si entro a minar")
    registrar_progreso()
    bugeados = set()

    # Cargar templates una sola vez
    #_tmpl_rec  = cv2.imread("recolectar.png",   cv2.IMREAD_COLOR)
    #_tmpl_rec2 = cv2.imread("recolectar-2.png", cv2.IMREAD_COLOR)
    #_h_rec, _w_rec = _tmpl_rec.shape[:2]
    UMBRAL_REC = 0.7
    _region = (0, 0, 1280, 1024)

    while True:
        recnec()
        ventana_nivel()
        posiciones_activas = [p for p in posiciones if p not in bugeados]
        if not posiciones_activas:
            print("⚠️ Todos los minerales de la sala están bugeados. Pasando a la siguiente sala.")
            break

        encontro_mineral = False
        vent_pelea()  # una sola vez por barrido
        inter()

        for x, y in posiciones_activas:
            ventana_nivel()
            # Clic en la posición del mineral
            heart.click(x, y)
            time.sleep(0.2)  # reducido de 0.4 a 0.2

            # Screenshot y comparación de templates
            _ss = cv2.cvtColor(np.array(pyautogui.screenshot(region=_region)), cv2.COLOR_RGB2BGR)
            score_1, loc_1 = _score_imagen_tmpl(_tmpl_rec,  _ss)
            score_2, _     = _score_imagen_tmpl(_tmpl_rec2, _ss) if _tmpl_rec2 is not None else (0.0, None)

            # Ninguna imagen visible → no hay mineral
            if score_1 < UMBRAL_REC and score_2 < UMBRAL_REC:
                heart.moveTo(150, 400)
                continue

            # recolectar-2 ganó → mineral no disponible por nivel
            if score_2 >= UMBRAL_REC and score_2 > score_1:
                print(f"⚠️ ({x},{y}) no disponible por nivel bajo")
                heart.moveTo(150, 400)
                continue

            # recolectar.png ganó → mineral disponible
            pos_recolectar = (loc_1[0] + _w_rec // 2, loc_1[1] + _h_rec // 2)

            # --- Mineral encontrado ---
            print(f"⛏️ Mineral en ({x}, {y})")
            encontro_mineral = True

            # Click inmediato sobre recolectar sin delays intermedios
            heart.click(pos_recolectar[0], pos_recolectar[1])
            recnec()
            ventana_nivel()
            vent_pelea()
            time.sleep(1)

            # RGB base en la posición del mineral
            color_base = heart.pixel(x, y)
            heart.moveTo(150, 400)
            espera = 0

            while True:
                inter()
                vent_pelea()
                color_actual = heart.pixel(x, y)

                # El mineral cambió de color → fue recolectado
                if any(abs(color_actual[i] - color_base[i]) > 3000 for i in range(3)):
                    print("⛏️ Salgo de minar")
                   
                    recnec()
                    break

                if heart.pixelMatchesColor(1264, 622, (255, 33, 33), tolerance=10):
                    time.sleep(2)
                    
                    recnec()
                    break

                espera += 1
                time.sleep(.2)

                if espera == 30:
                    print(f"⚠️ Mineral bugeado en ({x},{y}) — ignorando esta visita")
                    bugeados.add((x, y))
                    break

            break  # reiniciar desde posición 0

        if not encontro_mineral:
            break

def minar(posiciones):
    t_minar_start = time.time()
    print(f"[MINAR] ▶️ inicio | {len(posiciones)} posiciones configuradas")
    registrar_progreso()
    bugeados = set()
    minerales_minados = [0]  # contador mutable accesible desde closures

    _tmpl_rec  = cv2.imread(os.path.join(_DIR, "recolectar.png"),   cv2.IMREAD_COLOR)
    _tmpl_rec2 = cv2.imread(os.path.join(_DIR, "recolectar-2.png"), cv2.IMREAD_COLOR)  # falso positivo (guión)
    _tmpl_rec3 = cv2.imread(os.path.join(_DIR, "recolectar_2.png"), cv2.IMREAD_COLOR)  # mineral válido (guión bajo)
    if _tmpl_rec is None:
        raise FileNotFoundError(f"No se pudo cargar la plantilla de recolectar: {_DIR}\\recolectar.png")
    _h_rec,  _w_rec  = _tmpl_rec.shape[:2]
    _h_rec3, _w_rec3 = _tmpl_rec3.shape[:2] if _tmpl_rec3 is not None else (0, 0)
    UMBRAL_REC = 0.65
    _region = (331, 143, 948, 554)
    _off_x, _off_y = 331, 143
    CLICK_LIMPIAR = (921, 835)

    # PyAutoGUI inyecta un PAUSE de 0.1s por default después de CADA click/moveTo.
    # En un scan de 10 posiciones son 1s escondido. Lo bajamos al mínimo seguro.
    _pause_orig = pyautogui.PAUSE
    pyautogui.PAUSE = 0.02
    print(f"[MINAR] pyautogui.PAUSE {_pause_orig} -> {pyautogui.PAUSE}")

    def _evaluar_screenshot(ss):
        """Evalúa las 3 plantillas sobre un screenshot ya capturado.
        Retorna (score_1, loc_1, score_2, score_3, loc_3)."""
        s1, l1 = _score_imagen_tmpl(_tmpl_rec,  ss)
        s2, _  = _score_imagen_tmpl(_tmpl_rec2, ss) if _tmpl_rec2 is not None else (0.0, None)
        s3, l3 = _score_imagen_tmpl(_tmpl_rec3, ss) if _tmpl_rec3 is not None else (0.0, None)
        return s1, l1, s2, s3, l3

    def check_mineral_en(x, y, tag="check"):
        """Click en (x,y), template match en región recortada.
        Retorna (encontrado, pos_recolectar_absoluta | None).
        Plantillas válidas: recolectar.png y recolectar_2.png (guión bajo).
        recolectar-2.png (guión) es falso positivo y descarta el match.
        Si el primer screenshot no detecta nada, hace un reintento tras 0.12s."""
        ventana_nivel()
        t0 = time.time()
        heart.click(x, y)
        time.sleep(0.13)  # aumentado de 0.08 → 0.13 para dar tiempo al juego
        _ss = cv2.cvtColor(np.array(pyautogui.screenshot(region=_region)), cv2.COLOR_RGB2BGR)
        score_1, loc_1, score_2, score_3, loc_3 = _evaluar_screenshot(_ss)

        # Reintento solo si el score está cerca del umbral (foto llegó antes que la UI)
        # Score muy bajo (< 0.50) = mineral definitivamente ausente, no reintentar
        UMBRAL_REINTENTO = 0.50
        if score_1 < UMBRAL_REC and score_3 < UMBRAL_REC and (score_1 > UMBRAL_REINTENTO or score_3 > UMBRAL_REINTENTO):
            time.sleep(0.10)
            _ss2 = cv2.cvtColor(np.array(pyautogui.screenshot(region=_region)), cv2.COLOR_RGB2BGR)
            s1b, l1b, s2b, s3b, l3b = _evaluar_screenshot(_ss2)
            print(f"[{tag}] reintento s1={s1b:.2f} s3={s3b:.2f}")
            score_1, loc_1, score_2, score_3, loc_3 = s1b, l1b, s2b, s3b, l3b

        dur = time.time() - t0

        # Ninguna plantilla válida supera el umbral
        if score_1 < UMBRAL_REC and score_3 < UMBRAL_REC:
            print(f"[{tag}] ({x},{y}) vacío — s1={score_1:.2f} s2={score_2:.2f} s3={score_3:.2f} ({dur*1000:.0f}ms)")
            heart.moveTo(150, 400)
            return False, None
        # Falso positivo: recolectar-2.png (guión) domina sobre ambas válidas
        if score_2 >= UMBRAL_REC and score_2 > score_1 and score_2 > score_3:
            print(f"[{tag}] ⚠️ ({x},{y}) falso positivo recolectar-2 — s2={score_2:.2f} ({dur*1000:.0f}ms)")
            heart.moveTo(150, 400)
            return False, None

        # Elegir la plantilla válida con mayor score para obtener la posición
        if score_1 >= UMBRAL_REC and score_1 >= score_3:
            pos_recolectar = (loc_1[0] + _off_x + _w_rec  // 2,
                              loc_1[1] + _off_y + _h_rec  // 2)
            print(f"[{tag}] ✅ ({x},{y}) MINERAL (rec1) — s1={score_1:.2f} s3={score_3:.2f} pr={pos_recolectar} ({dur*1000:.0f}ms)")
        else:
            pos_recolectar = (loc_3[0] + _off_x + _w_rec3 // 2,
                              loc_3[1] + _off_y + _h_rec3 // 2)
            print(f"[{tag}] ✅ ({x},{y}) MINERAL (rec3) — s1={score_1:.2f} s3={score_3:.2f} pr={pos_recolectar} ({dur*1000:.0f}ms)")
        return True, pos_recolectar

    _scan_idx = [0]  # índice circular: el próximo scan arranca desde aquí

    def scan_circular(desde, excluir=None, tag="SCAN"):
        """Scan circular sobre posiciones desde índice 'desde'.
        Al encontrar un mineral actualiza _scan_idx al índice siguiente.
        Retorna (x, y, pos_recolectar) o None."""
        n = len(posiciones)
        t0 = time.time()
        revisadas = 0
        ventana_nivel()
        for offset in range(n):
            i = (desde + offset) % n
            x, y = posiciones[i]
            if (x, y) in bugeados:
                continue
            if excluir and (x, y) == excluir:
                continue
            ventana_nivel()
            revisadas += 1
            found, pr = check_mineral_en(x, y, tag=tag)
            if found:
                _scan_idx[0] = (i + 1) % n
                print(f"[{tag}] 🎯 mineral idx={i} ({x},{y}) tras {revisadas} rev | {(time.time()-t0)*1000:.0f}ms | prox_idx={_scan_idx[0]}")
                return (x, y, pr)
        print(f"[{tag}] ❌ sin minerales ({revisadas} rev | {(time.time()-t0)*1000:.0f}ms)")
        return None

    UMBRAL_DEPLETION = 30  # delta RGB por canal que indica que el mineral cambió

    def depletion_detectado(x_act, y_act, color_base):
        color_actual = heart.pixel(x_act, y_act)
        return any(abs(color_actual[i] - color_base[i]) > UMBRAL_DEPLETION for i in range(3))

    def minar_y_esperar_con_scan(x_act, y_act, pr_act):
        """Click en pr_act, inicia recolección, espera depletion.
        Durante la espera hace UNA pasada circular acumulando TODOS los minerales
        encontrados en next_queue (no para en el primero).
        Retorna lista de (x, y, pos_recolectar) — vacía si no encontró nada."""
        t_start = time.time()
        print(f"[MINE] ⛏️ iniciar recolección en ({x_act},{y_act}) via pr={pr_act}")
        heart.click(pr_act[0], pr_act[1])
        recnec()
        ventana_nivel()
        vent_pelea()
        time.sleep(0.2)

        color_base = heart.pixel(x_act, y_act)
        print(f"[MINE] baseline RGB={color_base} capturado a los {(time.time()-t_start)*1000:.0f}ms")
        heart.moveTo(150, 400)
        next_queue = []        # cola: todos los minerales encontrados durante el scan
        scan_realizado = False
        t_scan_end = None
        t_espera_inicio = time.time()
        t_ultimo_heartbeat = time.time()
        iteraciones = 0

        MAX_POST_SCAN = 10.0
        MAX_ESPERA_TOTAL = 30.0
        HEARTBEAT_SEGS = 1.0

        try:
            while True:
                iteraciones += 1
                inter()
                vent_pelea()

                color_actual = heart.pixel(x_act, y_act)
                delta = max(abs(color_actual[i] - color_base[i]) for i in range(3))

                if delta > UMBRAL_DEPLETION:
                    minerales_minados[0] += 1
                    print(f"[MINE] 💨 depletion en ({x_act},{y_act}) | delta={delta} | minados={minerales_minados[0]} | cola={len(next_queue)}")
                    pelear2()
                    recnec()
                    print(f"[MINE] post pelear2+recnec = {(time.time()-t_start)*1000:.0f}ms")
                    return next_queue

                if heart.pixelMatchesColor(1264, 622, (255, 33, 33), tolerance=10):
                    print("[MINE] pixel (1264,622) rojo — abort")
                    time.sleep(2)
                    pelear2()
                    recnec()
                    return next_queue

                # Scan circular: acumula TODOS los minerales encontrados, no para en el primero
                if not scan_realizado:
                    n_pos = len(posiciones)
                    inicio_scan = _scan_idx[0]
                    print(f"[MINE] 🔍 scan lineal desde idx={inicio_scan} hasta el final ({n_pos - inicio_scan} pos) a los {(time.time()-t_start)*1000:.0f}ms")
                    t_scan = time.time()
                    revisadas = 0
                    depletion_mid_scan = False
                    last_found_i = -1
                    limpiar_clickeado = False
                    for i in range(inicio_scan, n_pos):  # lineal: sin wrap a pos 0
                        x, y = posiciones[i]
                        if (x, y) in bugeados or (x, y) == (x_act, y_act):
                            continue
                        if not depletion_mid_scan:
                            c_scan = heart.pixel(x_act, y_act)
                            d_scan = max(abs(c_scan[k] - color_base[k]) for k in range(3))
                            if d_scan > UMBRAL_DEPLETION:
                                minerales_minados[0] += 1
                                print(f"[MINE] 💨 depletion mid-scan idx={i} | delta={d_scan} | cola={len(next_queue)}")
                                pelear2()
                                recnec()
                                depletion_mid_scan = True
                                if next_queue:
                                    # ya hay minerales en espera → parar scan y minarlos
                                    print(f"[MINE] cola={len(next_queue)} → parando scan, ir a minar")
                                    break
                                # cola vacía → continuar scan para encontrar algo antes de salir
                        tag_scan = "SCAN-CONT" if depletion_mid_scan else "SCAN-PAR"
                        revisadas += 1
                        found, pr = check_mineral_en(x, y, tag=tag_scan)
                        if found:
                            next_queue.append((x, y, pr))
                            last_found_i = i
                            if not limpiar_clickeado:
                                heart.click(CLICK_LIMPIAR[0], CLICK_LIMPIAR[1])
                                time.sleep(0.03)
                                limpiar_clickeado = True
                            print(f"[MINE] 🎯 cola[{len(next_queue)}] idx={i} ({x},{y})")
                            # sin break: sigue acumulando
                    if last_found_i >= 0:
                        _scan_idx[0] = (last_found_i + 1) % n_pos
                    scan_realizado = True
                    t_scan_end = time.time()
                    print(f"[MINE] scan terminado | {(t_scan_end-t_scan)*1000:.0f}ms | revisadas={revisadas} | cola={len(next_queue)} | prox_idx={_scan_idx[0]}")
                    if depletion_mid_scan:
                        return next_queue

                # --- Timeouts ---
                ahora = time.time()

                if ahora - t_ultimo_heartbeat >= HEARTBEAT_SEGS:
                    fase = "POST-SCAN" if scan_realizado else "PRE-SCAN"
                    print(f"[MINE] ⏱️ {fase} delta={delta} elapsed={(ahora-t_espera_inicio):.1f}s cola={len(next_queue)}")
                    t_ultimo_heartbeat = ahora

                if scan_realizado and t_scan_end is not None:
                    if ahora - t_scan_end > MAX_POST_SCAN:
                        print(f"[MINE] ⚠️ timeout post-scan: ({x_act},{y_act}) bugeado | delta={delta}")
                        bugeados.add((x_act, y_act))
                        return next_queue

                if ahora - t_espera_inicio > MAX_ESPERA_TOTAL:
                    print(f"[MINE] ⚠️ timeout duro: ({x_act},{y_act}) bugeado | delta={delta}")
                    bugeados.add((x_act, y_act))
                    return next_queue

                time.sleep(.08)
        except Exception as e:
            import traceback
            print(f"[MINE] 💥 EXCEPCIÓN en minar_y_esperar_con_scan: {type(e).__name__}: {e}")
            print(f"[MINE] traceback:\n{traceback.format_exc()}")
            raise

    # --- Loop principal ---
    try:
        while True:
            try:
                recnec()
                ventana_nivel()
            except Exception as e:
                import traceback
                print(f"[MINAR] 💥 excepción en recnec/ventana_nivel: {type(e).__name__}: {e}")
                print(traceback.format_exc())
                raise
            posiciones_activas = [p for p in posiciones if p not in bugeados]
            if not posiciones_activas:
                print("[MINAR] ⚠️ todas las posiciones bugeadas, salgo")
                break

            vent_pelea()
            inter()

            info = scan_circular(_scan_idx[0], tag="SCAN-INI")
            if info is None:
                print("[MINAR] ❌ pasada completa sin minerales, salgo")
                break

            idx_antes = _scan_idx[0]
            next_queue = minar_y_esperar_con_scan(*info)

            # Cola: procesar todos los minerales acumulados durante el scan
            while next_queue:
                x, y, _ = next_queue.pop(0)
                t_reverif = time.time()
                print(f"[CADENA] re-verificando ({x},{y}) | {len(next_queue)} restantes en cola")
                found, pr = check_mineral_en(x, y, tag="RE-VERIF")
                print(f"[CADENA] re-verif en {(time.time()-t_reverif)*1000:.0f}ms | found={found}")
                if found:
                    nuevos = minar_y_esperar_con_scan(x, y, pr)
                    next_queue = next_queue + nuevos
                else:
                    print(f"[CADENA] ({x},{y}) ya no disponible, continúa con cola={len(next_queue)}")

            # Cola agotada: solo continúa si el rescan llegó hasta la última posición
            # (cubrió todo el rango → _scan_idx wrapeó a 0 o menor que el inicio)
            if _scan_idx[0] < idx_antes or _scan_idx[0] == 0:
                print(f"[MINAR] rescan cubrió hasta el final → una pasada más desde idx=0")
                _scan_idx[0] = 0
            else:
                print(f"[MINAR] cola agotada, rescan no cubrió todo → saliendo")
                break
    finally:
        pyautogui.PAUSE = _pause_orig
        print(f"[MINAR] ⏹️ fin | duración total {(time.time()-t_minar_start):.2f}s | minerales minados={minerales_minados[0]} | PAUSE restaurado a {_pause_orig}")

    return minerales_minados[0]

# ---------------------------------------------------------------------------
# Watchdog de pasadas vacías por sala.
# Si una misma sala recorre sus posiciones MAX_PASADAS_VACIAS veces seguidas
# sin minar nada, se asume que el bot quedó pegado y se dispara reorientación.
# No afecta el comportamiento de minar(): solo envuelve la llamada.
# ---------------------------------------------------------------------------
_PASADAS_VACIAS = {}
MAX_PASADAS_VACIAS = 5
REORIENTAR_HABILITADO = False  # deshabilitado: disparaba reorientaciones en minas naturalmente vacías

def minar_ws(posiciones, sala_id, nombre_mina=""):
    """Llama a minar() y actualiza el watchdog de pasadas vacías para `sala_id`.

    Retorna True si se cumplió la condición de bot pegado y ya se ejecutó
    la reorientación (vent_pelea + inter + caminarMina + pelear2). El caller
    debe hacer `break` para salir del while de la sub-sala.
    """
    minados = minar(posiciones)
    if minados == 0:
        _PASADAS_VACIAS[sala_id] = _PASADAS_VACIAS.get(sala_id, 0) + 1
        print(f"[WATCHDOG] sala={sala_id} pasada vacía #{_PASADAS_VACIAS[sala_id]}/{MAX_PASADAS_VACIAS}")
        if _PASADAS_VACIAS[sala_id] >= MAX_PASADAS_VACIAS:
            if REORIENTAR_HABILITADO:
                print(f"⚠️ Bot pegado en {nombre_mina} sala={sala_id} — reorientando")
                _PASADAS_VACIAS[sala_id] = 0
                vent_pelea()
                inter()
                caminarMina()
                pelear2()
                return True
            else:
                print(f"[WATCHDOG] sala={sala_id} umbral alcanzado — reorientación DESHABILITADA (solo log)")
                _PASADAS_VACIAS[sala_id] = 0
    else:
        if _PASADAS_VACIAS.get(sala_id, 0) > 0:
            print(f"[WATCHDOG] sala={sala_id} reset (minados={minados})")
        _PASADAS_VACIAS[sala_id] = 0
    return False

def minar_2(posiciones):
    print("si entro a minar")
    bugeados = set()      # posiciones bugeadas en esta visita a la sala
    ultimo_vacio = {}     # {(x,y): timestamp} — posiciones confirmadas vacías recientemente
    SKIP_SECS = 10.0      # segundos antes de re-verificar una posición vacía

    while True:
        recnec()

        posiciones_activas = [p for p in posiciones if p not in bugeados]
        if not posiciones_activas:
            print("⚠️ Todos los minerales de la sala están bugeados. Pasando a la siguiente sala.")
            break

        encontro_mineral = False
        ahora = time.time()

        for x, y in posiciones_activas:
            # Posición recién vista vacía → saltar sin leer pixel
            if ahora - ultimo_vacio.get((x, y), 0) < SKIP_SECS:
                continue

            vent_pelea()
            color = heart.pixel(x, y)

            if not any(v > 120 for v in color):
                ultimo_vacio[(x, y)] = ahora  # confirmar vacío con timestamp
                continue

            # --- Mineral encontrado ---
            print(f"⛏️ Mineral en ({x}, {y})")
            encontro_mineral = True
            recnec()
            ventana_nivel()
            vent_pelea()
            inter()
            recolectar(x, y)

            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break

            heart.moveTo(150, 400)
            espera = 0

            while True:
                inter()
                vent_pelea()
                color = heart.pixel(x, y)

                if any(v < 80 for v in color):
                    print("⛏️ Salgo de minar")
                    vent_pelea()
                    pelear2()
                    recnec()
                    inter()
                    ventana_nivel()
                    ultimo_vacio[(x, y)] = time.time()
                    break

                if heart.pixelMatchesColor(1264, 622, (255, 33, 33), tolerance=10):
                    time.sleep(2)
                    vent_pelea()
                    pelear2()
                    inter()
                    break

                espera += 1
                time.sleep(.2)

                if espera == 30:
                    print(f"⚠️ Mineral bugeado en ({x},{y}) — ignorando esta visita")
                    bugeados.add((x, y))  # ignorar el resto de esta visita a la sala
                    break

            vent_pelea()
            inter()
            break  # reiniciar desde posición 0

        if not encontro_mineral:
            break
            
def minero(p):
    print(f"entra hablar {p}")
    while True:
        recnec()
        #mina pueblo (1040,  267)
        #-2,4 (703, 339)
        vuelta = 0
        hablar = [None,(1040,  267),(703, 339), (941,393), (557, 392), (809,291), (739,322), (1148, 330), (402 , 225), (771, 305 )]
        while True:
            
            x, y = hablar[p]
            heart.click(x,y)
            time.sleep(1)
            heart.click(x+15,y+13)
            time.sleep(2)
            if heart.pixelMatchesColor(665,318 ,(230, 230, 186), tolerance=10) and heart.pixelMatchesColor(598, 620 ,(230, 230, 186), tolerance=10):
                break
            recnec()
        if heart.pixelMatchesColor(683,  332, (255, 255, 206), tolerance=10):
            time.sleep(1)
            heart.click(590,  553)
            while True:
                recnec()
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    print("rimpe en sala minero")
                    break
            break
sadi = [os.path.join(_DIR, "dadi10.png")]
jala = [os.path.join(_DIR, f"jala{i}.png") for i in range(1, 11)]

def buscar_imagen_en_pantalla2(
        lista_imagenes,
        region_busqueda=(310, 132, 964, 580),
        umbral=0.5):

    for imagen in lista_imagenes:
        if not os.path.isabs(imagen):
            imagen = os.path.join(_DIR, imagen)
        # Cargar la imagen del template
        if not os.path.exists(imagen):
            print(f"[ERROR] Archivo no existe: {imagen}")
        else:
            print(f"[DEBUG] Leyendo plantilla: {imagen}")
        template = cv2.imread(imagen, cv2.IMREAD_UNCHANGED)
        if template is None:
            print(f"[ERROR] No se pudo cargar la imagen {imagen}")
            continue

        # Si tiene 4 canales (RGBA) → convertir a BGR
        if template.shape[2] == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

        # Capturar pantalla
        screenshot = pyautogui.screenshot(region=region_busqueda)
        screenshot = np.array(screenshot)

        # screenshot viene como RGB → convertir a BGR
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # Asegurar que ambos tienen mismo tipo
        if template.dtype != screenshot.dtype:
            template = template.astype(screenshot.dtype)

        # Match template
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        # Si encuentra coincidencia válida
        if max_val >= umbral:
            x, y = max_loc
            x += region_busqueda[0]
            y += region_busqueda[1]

            w, h = template.shape[1], template.shape[0]
            return (x + w // 2, y + h // 2)

    # Si no encuentra nada → devolver (555,555)
    heart.click(1145, 213,clicks=2,interval=.2)
    time.sleep(.2)
    heart.click(1140, 180,clicks=2,interval=.2)
    time.sleep(.2)
    heart.click(1212, 213,clicks=2,interval=.2)
    return (555,555)
def enemigo_mas_lejano_al_aliado2(lista_enemigo, lista_aliado,
                                 region_busqueda=(310, 132, 964, 580), 
                                 umbral=0.5, debug=False):

    # ---------------------------
    # Capturar screenshot en 3 canales (BGR)
    # ---------------------------
    screenshot = np.array(pyautogui.screenshot(region=region_busqueda))
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # ---------------------------
    # Función interna para cargar imágenes y convertir RGBA → BGR
    # ---------------------------
    def cargar_template(ruta):
        img = cv2.imread(ruta, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"[ERROR] No se pudo cargar {ruta}")
            return None

        # Si tiene canal alpha, convertir a 3 canales
        if len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img

    # ---------------------------
    # Buscar aliado (usando lista de imágenes)
    # ---------------------------
    pos_aliado = None
    mejor_val_aliado = 0

    for img_aliado in lista_aliado:

        template_aliado = cargar_template(img_aliado)
        if template_aliado is None:
            continue

        res = cv2.matchTemplate(screenshot, template_aliado, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val > umbral and max_val > mejor_val_aliado:
            mejor_val_aliado = max_val

            w, h = template_aliado.shape[1], template_aliado.shape[0]
            pos_aliado = (max_loc[0] + region_busqueda[0] + w // 2,
                          max_loc[1] + region_busqueda[1] + h // 2)

            if debug:
                print(f"[ALIADO] Detectado {img_aliado} en {pos_aliado} val={max_val}")

    if pos_aliado is None:
        if debug:
            print("[ALIADO] No se encontró ningún aliado.")
        return (555,555)

    # ---------------------------
    # Buscar enemigos (usando lista de imágenes)
    # ---------------------------
    enemigos_detectados = []

    for img_enemigo in lista_enemigo:

        template_enemigo = cargar_template(img_enemigo)
        if template_enemigo is None:
            continue

        res = cv2.matchTemplate(screenshot, template_enemigo, cv2.TM_CCOEFF_NORMED)
        _, max_val_e, _, max_loc_e = cv2.minMaxLoc(res)

        if max_val_e < umbral:
            continue

        w, h = template_enemigo.shape[1], template_enemigo.shape[0]
        x = max_loc_e[0] + region_busqueda[0] + w // 2
        y = max_loc_e[1] + region_busqueda[1] + h // 2
        enemigos_detectados.append((x, y))

        if debug:
            print(f"[ENEMIGO] {img_enemigo} en {(x, y)} val={max_val_e:.2f}")

    if not enemigos_detectados:
        if debug:
            print("[ENEMIGO] No se encontró ningún enemigo.")
        return (555,555)

    # ---------------------------
    # Buscar enemigo MÁS LEJANO al aliado
    # ---------------------------
    enemigo_lejano = max(
        enemigos_detectados,
        key=lambda e: math.dist(pos_aliado, e)
    )

    if debug:
        print(f"[RESULTADO] Enemigo más lejano: {enemigo_lejano}")

    return enemigo_lejano

def sala():
    if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
        any_desk()
        while heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10):
            heart.click(
                random.randint(835 - 20, 835 + 20),
                random.randint(491 - 20, 491 + 20)
)

            recnec()   
            time.sleep(.3)
            heart.press("z")
            any_desk()
            print("sala para peliar con minros")
            encontrado = False
            consal = 0
            while  True: #heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                #caminando
                heart.keyDown("z")
                consal = consal + 1
                if consal == 200:
                    break
                print(consal)
                recnec()
                if heart.pixelMatchesColor( 440 , 435 , (230, 230, 186), tolerance=5):
                    time.sleep(.5)
                    heart.click(764,324)
                if heart.pixelMatchesColor( 425,295, (249, 247, 242), tolerance=5):
                    time.sleep(.5)
                    heart.click( 762 ,329)    
                #heart.click(1130,436)
                recnec()
                any_desk()
                registrar_progreso()
                print("buscando mineros")
                
                inter()
                #pelear3()
                #heart.keyDown("m")
                post = detectar_enemigo_sala(r"nivel-minero.png", debug=True)
                
                    
                    
                while post and not encontrado:
                    x,y= post
                    heart.click(x+11,y+57, button="left")
                    consal = 0  
                    
                    
                    time.sleep(1.5)
                    
                    encontrado = True
                       
                if  encontrado:
                    print("Enemigo desapareció. Volviendo a buscar...")
                    encontrado = False
                time.sleep(.1)
                
                if heart.pixelMatchesColor(1184 , 635 , (176, 184, 147), tolerance=10) or  heart.pixelMatchesColor(1264,623 , (255,  33,  33), tolerance=10):
                        print("deja de caminar")
                        heart.keyUp("z")
                        pelear3()
                        break
            cont = 0
            while True:
                time.sleep(.1)
                cont = cont + 1
                if cont == 200:
                    break
                ventana_nivel()
                vent_pelea()
                pelear3()
                
                print("esperando hablar con minero o zap---")
                recnec()
                #heart.click(1044, 820, clicks=2,interval=.2)
                if  heart.pixelMatchesColor(668,656, (230, 224, 205), tolerance=10):
                   # heart.click(1044, 820, clicks=2,interval=.2)
                    break
                if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5):
                    #heart.click(1044, 820, clicks=2,interval=.2)
                    break
                if  heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :  
                   # heart.click(1044, 820, clicks=2,interval=.2)
                    recnec()
                    any_desk()    
                    
                    
                    
                    #heart.click(1043, 821, 2, interval=.2 )
                    
                    
                    while  True:
                        ventana_nivel()
                        vent_pelea()
                        recnec()
                        print("esta aca")
                        if  heart.pixelMatchesColor(821 , 458 , (207, 205, 183), tolerance=10):   
                            
                            break
                        
                        while  heart.pixelMatchesColor(590, 363 , (146, 108,  46), tolerance=10):
                            heart.click(939, 365)
                            time.sleep(.3)
                            
                            heart.click(969,377)
                            time.sleep(.5)
                            if  heart.pixelMatchesColor(504, 263,(171, 118,  67), tolerance=10):
                                heart.press("esc")
                                time.sleep(3)
                                
                                

                            
                        
                        if  heart.pixelMatchesColor(773,  418,(230, 230, 186), tolerance=10):   
                            time.sleep(.3)
                            heart.click(742,438)
                            break
                        if  heart.pixelMatchesColor(834, 462 , (215, 206, 189), tolerance=10):   
                            time.sleep(.3)
                            
                            break
                        
                            
                    
                    while True:
                        ventana_nivel()
                        vent_pelea()
                        if  heart.pixelMatchesColor(821,  458 , (207, 205, 183), tolerance=10):   
                            
                            break
                        if  heart.pixelMatchesColor(834, 462 , (215, 206, 189), tolerance=10):   
                            time.sleep(.3)
                            
                            break
                        if  heart.pixelMatchesColor(724 , 435 , (230, 230, 186), tolerance=10):
                            print("vuelve a la sala a buscar mineros")
                            time.sleep(.5)
                            heart.click(760, 328 )
                            time.sleep(.2)
                            break
                        #sala()
                        print("despues caca")
                        if not heart.pixelMatchesColor(879,792, ( 94,  52,   7), tolerance=10):
                            time.sleep(.5)
                            break

                    break
            # el while externo re-evalúa la condición de sala automáticamente
TIEMPO_LIMITE = 60*60*6  # 6 horas en segundos

# ============================================================================
# REINICIO AUTOMÁTICO DEL JUEGO
# ============================================================================
def forzar_foco(hwnd):
    """Fuerza una ventana al frente aunque otra tenga el foco (bypass restricción Windows)."""
    import ctypes, win32gui, win32con
    user32 = ctypes.windll.user32
    foreground = user32.GetForegroundWindow()
    tid_foreground = user32.GetWindowThreadProcessId(foreground, 0)
    tid_target = user32.GetWindowThreadProcessId(hwnd, 0)
    user32.AttachThreadInput(tid_target, tid_foreground, True)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(tid_target, tid_foreground, False)


def reiniciar_juego():
    """
    Cierra el juego, abre el launcher, clickea JUGAR, maximiza la ventana y reconecta.
    Itera indefinidamente ante cualquier fallo hasta lograr una recnec() exitosa.
    """
    import pygetwindow as gw
    global _dentro_de_reiniciar, _bot_reiniciando
    _dentro_de_reiniciar = True

    def _matar_juego():
        for title in gw.getAllTitles():
            if ('dofus' in title.lower() or 'retro' in title.lower()) and 'ankama' not in title.lower():
                for w in gw.getWindowsWithTitle(title):
                    try:
                        w.close()
                    except Exception:
                        pass
        for nombre in ['Dofus.exe', 'dofus.exe', 'retro.exe', 'Retro.exe']:
            subprocess.call(['taskkill', '/f', '/im', nombre],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Juego cerrado. Esperando 5s...")
        time.sleep(5)

    def _abrir_launcher():
        launcher_win = None
        for title in gw.getAllTitles():
            if 'ankama' in title.lower() and 'dofus' not in title.lower():
                wins = gw.getWindowsWithTitle(title)
                if wins:
                    launcher_win = wins[0]
                    break
        if launcher_win:
            forzar_foco(launcher_win._hWnd)
            time.sleep(1)
            print("Launcher encontrado y activado.")
        else:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut = os.path.join(desktop, "Dofus Retro.lnk")
            print(f"Abriendo launcher desde: {shortcut}")
            os.startfile(shortcut)
            time.sleep(12)

    def _click_jugar():
        pyautogui.press('escape')
        time.sleep(1)
        for _ in range(45):
            jugar = buscar_imagen_en_inventario("jugar-boton.png")
            if jugar:
                time.sleep(1)
                heart.click(jugar[0], jugar[1])
                print(f"Click en JUGAR ({jugar[0]}, {jugar[1]})")
                return True
            time.sleep(2)
        print("⚠️ Botón JUGAR no encontrado.")
        return False

    def _maximizar_ventana():
        """Espera hasta 60s a que aparezca la ventana y la maximiza. Retorna hwnd o None."""
        for _ in range(30):
            for title in gw.getAllTitles():
                if ('dofus' in title.lower() or 'retro' in title.lower()) and 'ankama' not in title.lower():
                    wins = gw.getWindowsWithTitle(title)
                    if not wins:
                        continue
                    hwnd = wins[0]._hWnd
                    try:
                        forzar_foco(hwnd)
                    except Exception as e:
                        print(f"forzar_foco falló ({e}) — usando fallback")
                        try:
                            wins[0].activate()
                        except Exception:
                            pass
                    time.sleep(0.5)
                    try:
                        pyautogui.hotkey('win', 'up')
                    except Exception:
                        import win32gui, win32con
                        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    time.sleep(2)
                    print(f"Ventana '{title}' maximizada.")
                    return hwnd
            time.sleep(2)
        print("⚠️ Ventana del juego no encontrada tras 60s.")
        return None

    try:
        while True:
            try:
                # Cerrar TODAS las instancias antes de cada intento
                _matar_juego()

                # Abrir launcher y clickear JUGAR
                _abrir_launcher()
                if not _click_jugar():
                    print("🔄 No se encontró JUGAR — reintentando...")
                    continue

                # Esperar y maximizar la ventana del juego
                time.sleep(6)
                hwnd = _maximizar_ventana()
                if hwnd is None:
                    print("🔄 Ventana no apareció — reintentando...")
                    continue

                # Intentar reconexión
                _bot_reiniciando = False
                recnec()
                if not _bot_reiniciando:
                    print("✅ reiniciar_juego: reconexión exitosa")
                    return True

                print("🔄 recnec falló — reintentando...")

            except Exception as e:
                print(f"⚠️ Error inesperado en reiniciar_juego: {e} — reintentando...")

    finally:
        _dentro_de_reiniciar = False
# ============================================================================


# ---------------------------------------------------------------------------
# Navegación hacia el mercado (punto de venta)
# Mapa 1 (sala interior)  → clic (535,571) → Mapa 2 (exterior jardín)
# Mapa 2 (exterior jardín) → clic (1264,556) → Mapa 3 (mercado/subasta)
#
# PIXELS DE DETECCIÓN — verificar con ver_rgb.py si alguno no cuadra:
#   Mapa 1: suelo interior baldosa amarilla en (700,430) ≈ (200,185,140)
#            pared marrón derecha en (950,220)            ≈ (110, 80, 45)
#   Mapa 2: empedrado exterior gris-verde en (700,480)   ≈ (130,120, 90)
#            hierba/valla en (600,500)                    ≈ ( 90,110, 60)
#   Mapa 3: estructura mercado madera oscura en (750,350) ≈ ( 80, 60, 35)
#            cajas/cajones base en (700,480)              ≈ (100, 75, 40)
# ---------------------------------------------------------------------------
# ── variables fijas del almacén e inventario — modificar según la cuenta ── venta de mineral
MAXIMO_SLOTS       = 27 # slots disponibles en el almacén del mercado
CAPACIDAD_INVENTARIO = 7  # lotes máximos que puede cargar el personaje a la vez

def obtener_elementos_en_venta(debug=False, max_intentos=3):
    def _ocr_region(region, zoom=3, whitelist=True):
        ss = heart.screenshot(region=region)
        raw = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2GRAY)
        img = cv2.resize(raw, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        cfg = '--psm 7 -c tessedit_char_whitelist=0123456789()/' if whitelist else '--psm 7'
        return pytesseract.image_to_string(img, config=cfg), raw, img

    for intento in range(max_intentos):
        texto, img_raw, img_proc = _ocr_region((505, 283, 120, 36), whitelist=True)
        print(f"[OCR] texto leído (intento {intento+1}): '{texto.strip()}'")
        if debug and intento == 0:
            cv2.imwrite(os.path.join(_DIR, "debug_titulo.png"), img_proc)
            cv2.imwrite(os.path.join(_DIR, "debug_titulo_raw.png"), img_raw)
        m = re.search(r'\(?(\d{1,2})/', texto)
        if not m:
            # fallback región amplia — también con whitelist
            texto2, _, _ = _ocr_region((333, 283, 290, 36), whitelist=True)
            t2 = re.sub(r'[Oo]', '0', texto2)
            print(f"[OCR] fallback: '{texto2.strip()}'")
            m = re.search(r'\(?(\d{1,2})/', t2)
        if m:
            en_venta = int(m.group(1))
            espacios = MAXIMO_SLOTS - en_venta
            print(f"[OCR] en venta: {en_venta}/{MAXIMO_SLOTS} — espacios disponibles: {espacios}")
            return en_venta, MAXIMO_SLOTS, espacios
        if intento < max_intentos - 1:
            print(f"[OCR] no se leyó número — reintentando en 2s")
            time.sleep(2)
    print("[OCR] ⚠️ no se pudo leer el contador tras varios intentos")
    return None, None, None

def _cambiar_mapa(click_x, click_y, nombre, check_fn, max_intentos=4, timeout=15):
    for i in range(max_intentos):
        print(f"[nav] clic ({click_x},{click_y}) → {nombre} (intento {i+1}/{max_intentos})")
        heart.click(click_x, click_y)
        heart.moveTo(150, 400)
        if _esperar_mapa(nombre, check_fn, timeout=timeout):
            return True
        if i < max_intentos - 1:
            print(f"[nav] mapa no cambió — reintentando en 2s")
            time.sleep(2)
    print(f"[nav] ⚠️ no se pudo llegar a {nombre} tras {max_intentos} intentos")
    return False

def _esperar_mapa(nombre, check_fn, timeout=15):
    t0 = time.time()
    while True:
        recnec()
        if check_fn():
            print(f"[ir_mercado] mapa detectado: {nombre}")
            return True
        if time.time() - t0 > timeout:
            print(f"[ir_mercado] ⚠️ timeout esperando {nombre} ({timeout}s)")
            for x, y in [(700,430),(950,220),(700,480),(600,500),(750,350)]:
                print(f"    ({x},{y}) -> RGB{heart.pixel(x, y)}")
            return False
        time.sleep(0.3)

def _es_mapa1():
    return (heart.pixelMatchesColor(700, 430, (185, 157, 113), tolerance=20)
            and heart.pixelMatchesColor(950, 220, (132, 116,  34), tolerance=20))

def _es_mapa2():
    return (heart.pixelMatchesColor(700, 430, (185, 157, 113), tolerance=20) == False
            and heart.pixelMatchesColor(700, 480, (130, 120,  90), tolerance=30))

def _es_mapa3():
    return (heart.pixelMatchesColor(700, 430, (100,  67,  25), tolerance=20)
            and heart.pixelMatchesColor(700, 480, ( 69,  59,  30), tolerance=20))

def _lista_vacia():
    return heart.pixelMatchesColor(355, 395, (180, 172, 141), tolerance=15)

def retirar_minerales():
    X_MINERAL, Y_MINERAL = 358, 401
    X_RETIRAR, Y_RETIRAR = 385, 633
    retirados = 0
    print("[retirar] iniciando retirada hasta lista vacía...")
    while not _lista_vacia():
        heart.click(X_MINERAL, Y_MINERAL)
        time.sleep(0.5)
        heart.click(X_RETIRAR, Y_RETIRAR)
        time.sleep(1)
        retirados += 1
        print(f"[retirar] {retirados} retirado(s) — verificando lista...")
    print(f"[retirar] ✅ lista vacía tras {retirados} retirada(s)")

def leer_inventario(debug=False):
    region = (1009, 379, 251, 234)
    heart.click(1117, 338)
    time.sleep(0.5)
    ss = heart.screenshot(region=region)
    img_raw = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img_raw, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if debug:
        cv2.imwrite(os.path.join(_DIR, "debug_inventario.png"), img)
        cv2.imwrite(os.path.join(_DIR, "debug_inventario_raw.png"), img_raw)
        print("[inventario] imágenes debug guardadas")
    texto = pytesseract.image_to_string(img, config='--psm 6')
    print(f"[inventario] texto leído:\n{texto.strip()}")
    minerales = {}
    for linea in texto.splitlines():
        m = re.search(r'(\d{2,})\s+([A-Za-záéíóúÁÉÍÓÚñÑ]{3,})', linea)
        if m:
            minerales[m.group(2)] = int(m.group(1))
    print(f"[inventario] detectado: {minerales}")
    return minerales

def leer_precio_actual(debug=False):
    region = (872, 440, 138, 33)
    ss = heart.screenshot(region=region)
    img_raw = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img_raw, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    texto = pytesseract.image_to_string(img, config='--psm 7 -c tessedit_char_whitelist=0123456789')
    numero = re.sub(r'\D', '', texto.strip())
    if numero:
        precio = int(numero)
        print(f"[precio] {precio}")
        return precio
    print(f"[precio] ⚠️ no detectado, texto='{texto.strip()}'")
    return None

def vender_mineral(nombre, lotes):
    print(f"[vender] {nombre}: {lotes} lote(s) de 100")
    heart.click(1177, 393)
    time.sleep(1)
    precio_base = leer_precio_actual()
    if precio_base is None:
        print(f"[vender] ⚠️ precio no leído — abortando {nombre}")
        return False
    nuevo_precio = precio_base - 1
    print(f"[vender] precio base: {precio_base} → {nuevo_precio} (fijo para todos los lotes)")
    for i in range(lotes):
        if i > 0:
            heart.click(1177, 393)
            time.sleep(1)
        print(f"[vender] lote {i+1}/{lotes}")
        heart.click(910, 612)
        time.sleep(0.2)
        heart.hotkey('ctrl', 'a')
        heart.typewrite(str(nuevo_precio), interval=0.04)
        heart.click(738, 614)
        time.sleep(0.3)
        heart.click(748, 688)
        time.sleep(0.3)
        heart.press('enter')
        time.sleep(0.3)
        heart.press('enter')
        time.sleep(1)
    print(f"[vender] ✅ {nombre} completado — precio final: {nuevo_precio}")
    return True

def poner_todos_en_venta(inventario):
    if not inventario:
        print("[vender] inventario vacío")
        return
    for nombre, cantidad in inventario.items():
        lotes = cantidad // 100
        if lotes == 0:
            print(f"[vender] {nombre}: {cantidad} unidades — no alcanza lote de 100, omitiendo")
            continue
        vender_mineral(nombre, lotes)
        time.sleep(0.5)
    print("[vender] ✅ todos los minerales procesados")

def _ir_banco_venta():
    """Navega de vuelta al banco desde el mercado: mapa3→mapa2→mapa1.
    Reintenta cada paso hasta MAX_CICLOS veces evaluando el estado real en cada ciclo."""
    print("[ir_banco_venta] cerrando ventana de venta...")
    heart.press('escape')
    time.sleep(1.5)

    MAX_CICLOS = 6
    for ciclo in range(MAX_CICLOS):
        if _es_mapa1():
            print("[ir_banco_venta] ✅ llegó al banco")
            return True
        if _es_mapa3():
            print(f"[ir_banco_venta] ciclo {ciclo+1}: en mercado → yendo a mapa exterior")
            _cambiar_mapa(359, 401, "exterior jardín", _es_mapa2)
            time.sleep(0.5)
            continue
        if _es_mapa2():
            print(f"[ir_banco_venta] ciclo {ciclo+1}: en mapa exterior → yendo al banco")
            _cambiar_mapa(844, 341, "banco/sala interior", _es_mapa1)
            time.sleep(0.5)
            continue
        # Mapa no reconocido — esperar un momento y reintentar
        print(f"[ir_banco_venta] ciclo {ciclo+1}: mapa no reconocido — esperando...")
        _esperar_mapa_conocido(timeout=8)
        time.sleep(1)

    print("[ir_banco_venta] ⚠️ no se pudo llegar al banco tras todos los intentos")
    return False

MINERALES_ORDEN = [
    
    
    ('bauxita',   'bauxita'),
    ('oro',       'oro'),
    
    ('hierro',    'hierro'),
    ('plata',     'plata'),
    
]
REGION_BANCO = (348, 344, 216, 131)   # región calibrada con el banco abierto y filtro Mineral

def _leer_imagen(path):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)

def _buscar_todos_minerales_banco(haystack_gray):
    """Detecta todos los minerales a la vez con matriz de scores numpy.
    Usa 1 pico por mineral para que picos falsos no bloqueen posiciones de otros."""
    nombres_arch = [na for _, na in MINERALES_ORDEN]

    mmaps = {}
    for na in nombres_arch:
        path = os.path.join(_DIR, f"banco_{na}.png")
        if not os.path.exists(path): continue
        tmpl = _leer_imagen(path)
        if tmpl is None: continue
        if tmpl.shape[0] >= haystack_gray.shape[0] or tmpl.shape[1] >= haystack_gray.shape[1]: continue
        th, tw = tmpl.shape
        mmap = cv2.matchTemplate(haystack_gray, tmpl, cv2.TM_CCOEFF_NORMED)
        mmaps[na] = (mmap, th, tw)

    if not mmaps: return {}

    DIST_MIN  = 18
    candidatos = []
    for na, (mmap, th, tw) in mmaps.items():
        _, max_val, _, max_loc = cv2.minMaxLoc(mmap)
        if max_val < 0.60: continue
        r, c = max_loc[1], max_loc[0]
        if all(abs(r-er) > DIST_MIN or abs(c-ec) > DIST_MIN for er, ec in candidatos):
            candidatos.append((r, c))

    if not candidatos: return {}

    n       = len(MINERALES_ORDEN)
    n_cand  = len(candidatos)
    scores  = np.zeros((n, n_cand), dtype=np.float32)
    for i, na in enumerate(nombres_arch):
        if na not in mmaps: continue
        mmap, th, tw = mmaps[na]
        h_map, w_map = mmap.shape
        for j, (r, c) in enumerate(candidatos):
            if 0 <= r < h_map and 0 <= c < w_map:
                scores[i, j] = mmap[r, c]

    orden = np.dstack(np.unravel_index(np.argsort(scores.ravel())[::-1], scores.shape))[0]
    asignaciones    = {}
    candidatos_usados = set()
    for i, j in orden:
        score = float(scores[i, j])
        if score < 0.60: break
        na = nombres_arch[i]
        if na in asignaciones or j in candidatos_usados: continue
        r, c = candidatos[j]
        _, th, tw = mmaps[na]
        cx = REGION_BANCO[0] + c + tw // 2
        cy = REGION_BANCO[1] + r + th // 2
        asignaciones[na] = (cx, cy, score)
        candidatos_usados.add(j)

    return asignaciones


def _leer_portapapeles():
    try:
        root = tk.Tk()
        root.withdraw()
        texto = root.clipboard_get()
        root.destroy()
        return texto
    except Exception:
        return ''


def _leer_cantidad_drag(mineral_cx, mineral_cy, nombre):
    """Arrastra el mineral al slot de venta, lee la cantidad vía portapapeles y cancela."""
    DRAG_DESTINO = (1053, 368)
    CLICK_CAMPO  = (903,  352)
    CLICK_CERRAR = (946,  665)

    heart.moveTo(mineral_cx, mineral_cy, duration=0.5)
    time.sleep(0.3)
    heart.mouseDown(button='left')
    time.sleep(0.3)
    heart.moveTo(*DRAG_DESTINO, duration=0.7)
    time.sleep(0.2)
    heart.mouseUp(button='left')
    time.sleep(0.7)

    heart.click(*CLICK_CAMPO)
    time.sleep(0.5)
    heart.hotkey('ctrl', 'a')
    time.sleep(0.3)
    heart.hotkey('ctrl', 'c')
    time.sleep(0.4)

    texto = _leer_portapapeles()
    nums  = re.findall(r'\d+', texto)
    print(f"[banco] portapapeles {nombre}: {repr(texto)} → {nums}")
    resultado = int(max(nums, key=len)) if nums else 0

    for _ in range(3):
        heart.click(*CLICK_CERRAR)
        time.sleep(0.5)
    time.sleep(0.8)

    return resultado

def _clic_filtro_mineral(intentos=5, espera=1.5):
    template_path = os.path.join(_DIR, "mineral_filtro.png")
    if not os.path.exists(template_path):
        print("[banco] ⚠️ mineral_filtro.png no encontrado")
        return False
    template = _leer_imagen(template_path)
    if template is None:
        return False
    region = (350, 300, 400, 350)
    for intento in range(1, intentos + 1):
        ss = heart.screenshot(region=region)
        haystack = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2GRAY)
        res = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val >= 0.75:
            th, tw = template.shape
            cx = region[0] + max_loc[0] + tw // 2
            cy = region[1] + max_loc[1] + th // 2
            print(f"[banco] 'Mineral' encontrado en ({cx},{cy}) intento {intento}")
            heart.click(cx, cy)
            return True
        print(f"[banco] 'Mineral' no visible (max={max_val:.2f}) — espera {espera}s...")
        time.sleep(espera)
    print("[banco] ⚠️ 'Mineral' no encontrado tras todos los intentos")
    return False

def abrir_banco():
    print("[banco] abriendo banco...")
    time.sleep(2.5)
    heart.moveTo(947, 294, duration=0.5)
    time.sleep(0.5)
    heart.rightClick(947, 294)
    time.sleep(2.5)
    heart.click(467, 450)
    time.sleep(5.0)
    heart.click(421, 303)
    time.sleep(2.5)
    heart.click(476, 335)
    time.sleep(2.0)
    _clic_filtro_mineral(intentos=5, espera=1.5)
    time.sleep(1.5)
    print("[banco] filtro mineral activo")

def sacar_minerales_banco(espacios_libres):
    abrir_banco()
    lotes_restantes = min(espacios_libres, CAPACIDAD_INVENTARIO)
    print(f"[banco] espacios libres: {espacios_libres} — extrayendo máx {lotes_restantes} lote(s) (capacidad inventario={CAPACIDAD_INVENTARIO})")

    # Detectar todos los minerales de una sola captura
    ss       = heart.screenshot(region=REGION_BANCO)
    haystack = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2GRAY)
    asignaciones = _buscar_todos_minerales_banco(haystack)
    print(f"[banco] detectados: {[(n, f'{s:.2f}') for n,(x,y,s) in asignaciones.items()]}")

    for nombre_display, nombre_archivo in MINERALES_ORDEN:
        if lotes_restantes <= 0:
            break
        if nombre_archivo not in asignaciones:
            print(f"[banco] {nombre_display}: no detectado — omitiendo")
            continue

        cx, cy, score = asignaciones[nombre_archivo]
        print(f"[banco] {nombre_display}: pos=({cx},{cy}) conf={score:.2f}")

        # Leer cantidad vía drag al slot de venta + portapapeles
        cantidad = _leer_cantidad_drag(cx, cy, nombre_archivo)
        if cantidad < 100:
            print(f"[banco] {nombre_display}: {cantidad} unidades — insuficiente, omitiendo")
            continue

        lotes_posibles  = cantidad // 100
        lotes_a_extraer = min(lotes_posibles, lotes_restantes)
        a_extraer       = lotes_a_extraer * 100
        print(f"[banco] {nombre_display}: {cantidad} en banco → extrayendo {a_extraer} ({lotes_a_extraer} lote(s))")

        try:
            # Drag del mineral al inventario
            heart.moveTo(cx, cy, duration=0.5)
            time.sleep(0.3)
            heart.mouseDown(button='left')
            time.sleep(0.3)
            heart.moveTo(1178, 535, duration=1.0)
            time.sleep(0.3)
            heart.mouseUp(button='left')
            time.sleep(1.0)
            heart.hotkey('ctrl', 'a')
            time.sleep(0.3)
            heart.typewrite(str(a_extraer), interval=0.08)
            time.sleep(0.3)
            heart.press('enter')
            time.sleep(1.0)
            lotes_restantes -= lotes_a_extraer
        except Exception as e:
            print(f"[banco] ⚠️ error extrayendo {nombre_display}: {e}")

    print(f"[banco] ✅ extracción completa — {espacios_libres - lotes_restantes} lote(s) extraídos")
    heart.press('escape')
    time.sleep(0.5)

def _esperar_mapa_conocido(timeout=10):
    """Espera hasta timeout segundos a que el personaje esté en mapa1, 2 o 3."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        if _es_mapa1() or _es_mapa2() or _es_mapa3():
            return True
        time.sleep(1)
    px1a = heart.pixel(700, 430); px1b = heart.pixel(950, 220)
    px2  = heart.pixel(700, 480); px3b = heart.pixel(700, 480)
    print(f"[nav] ⚠️ mapa no reconocido tras {timeout}s — píxeles actuales:")
    print(f"  (700,430)={px1a}  (950,220)={px1b}  → mapa1 espera (185,157,113) y (132,116,34)")
    print(f"  (700,480)={px2}               → mapa2 espera (130,120,90)")
    print(f"  (700,480)={px3b}              → mapa3 espera (69,59,30) en (700,480)")
    return False

def _navegar_a_mercado():
    """Navega desde mapa1/2 hasta mapa3.
    Reintenta cada paso hasta MAX_CICLOS veces evaluando el estado real en cada ciclo."""
    MAX_CICLOS = 6
    for ciclo in range(MAX_CICLOS):
        if _es_mapa3():
            print("[nav→mercado] ✅ en mercado")
            return True
        if _es_mapa1():
            print(f"[nav→mercado] ciclo {ciclo+1}: en banco → yendo a mapa exterior")
            _cambiar_mapa(535, 571, "mapa exterior", _es_mapa2)
            time.sleep(0.5)
            continue
        if _es_mapa2():
            print(f"[nav→mercado] ciclo {ciclo+1}: en mapa exterior → yendo al mercado")
            _cambiar_mapa(1264, 556, "mercado", _es_mapa3)
            time.sleep(0.5)
            continue
        # Mapa no reconocido — esperar y reintentar
        print(f"[nav→mercado] ciclo {ciclo+1}: mapa no reconocido — esperando...")
        _esperar_mapa_conocido(timeout=8)
        time.sleep(1)

    print("[nav→mercado] ⚠️ no se pudo llegar al mercado tras todos los intentos")
    return False

def _abrir_ventana_comercio():
    """Abre la ventana de comercio en mapa3. Retorna espacios libres o None si falla."""
    time.sleep(0.5)
    heart.click(525, 464)
    time.sleep(0.5)
    heart.click(568, 504)
    time.sleep(2)
    en_venta, maximo, espacios = obtener_elementos_en_venta(debug=False)
    if en_venta is None:
        print("[mercado] ⚠️ no se pudo leer el contador de elementos")
        return None
    print(f"[mercado] en venta: {en_venta}/{maximo} — espacios libres: {espacios}")
    return espacios

def ir_mercado():
    heart.click(1159,820, clicks=2,interval=.2)  # click para asegurar foco en el jue
    print("[ir_mercado] iniciando navegación al mercado")
    heart.click(1155,820, clicks=2,interval=.2) 
    px1a = heart.pixel(700, 430); px1b = heart.pixel(950, 220)
    px2  = heart.pixel(700, 480)
    px3a = heart.pixel(700, 430); px3b = heart.pixel(700, 480)

    print(f"[ir_mercado] píxeles actuales:")
    print(f"  (700,430)={px1a}  (950,220)={px1b}  → mapa1 espera (185,157,113) y (132,116,34)")
    print(f"  (700,480)={px2}               → mapa2 espera (130,120,90)")
    print(f"  (700,430)={px3a}  (700,480)={px3b} → mapa3 espera (100,67,25) y (69,59,30)")

    if not _navegar_a_mercado():
        print("[ir_mercado] ⚠️ mapa actual no reconocido")
        return False

    # --- primera apertura: retirar minerales sin vender y vender inventario ---
    print("[ir_mercado] ✅ en mercado — abriendo ventana de comercio")
    espacios = _abrir_ventana_comercio()
    if espacios is None:
        return True

    if espacios < MAXIMO_SLOTS:
        print(f"[ir_mercado] hay minerales sin vender — retirando todos")
        retirar_minerales()

    inv = leer_inventario(debug=True)
    if inv:
        print(f"[ir_mercado] inventario: {inv}")
        poner_todos_en_venta(inv)
    else:
        print("[ir_mercado] ⚠️ inventario vacío o no detectado")

    # --- loop banco→mercado hasta llenar el almacén ---
    # La ventana de comercio queda ABIERTA tras cada venta.
    # Leemos el OCR directamente sin recliquear para no alterar el estado.
    # Solo reabrimos la ventana cuando venimos del banco (ventana fue cerrada).
    espacios_anteriores = MAXIMO_SLOTS + 1
    while True:
        # Ventana ya está abierta — leer OCR directamente
        time.sleep(4)  # dar tiempo al servidor para registrar la venta
        en_venta, _, espacios = obtener_elementos_en_venta(debug=False)
        if en_venta is None:
            print("[ir_mercado] ⚠️ OCR falló — terminando")
            break
        print(f"[ir_mercado] espacios libres: {espacios}")

        if espacios == 0:
            print("[ir_mercado] almacén lleno — terminando")
            break

        if espacios >= espacios_anteriores:
            print("[ir_mercado] banco sin minerales suficientes — terminando")
            break

        espacios_anteriores = espacios
        print(f"[ir_mercado] {espacios} espacios libres — yendo al banco")

        # _ir_banco_venta cierra la ventana con escape antes de navegar
        if not _ir_banco_venta():
            print("[ir_mercado] ⚠️ no se pudo llegar al banco")
            break

        sacar_minerales_banco(espacios)

        print("[ir_mercado] volviendo al mercado")
        if not _navegar_a_mercado():
            print("[ir_mercado] ⚠️ no se pudo volver al mercado")
            break

        # Ventana cerrada — abrirla de nuevo
        time.sleep(0.5)
        heart.click(525, 464)
        time.sleep(0.5)
        heart.click(568, 504)
        time.sleep(2)

        inv = leer_inventario(debug=False)
        if inv:
            print(f"[ir_mercado] poniendo en venta: {inv}")
            poner_todos_en_venta(inv)
        else:
            print("[ir_mercado] ⚠️ inventario vacío tras extracción del banco")
        # → vuelve al inicio del while, ventana sigue abierta, lee OCR directo

    heart.press('escape')
    time.sleep(2)

    heart.click(1080,820, clicks=2,interval=.2) 
    return True


# ============================================================================
# INICIALIZACIÓN DEL SISTEMA DE PATHFINDING PARA DOFUS RETRO
# ============================================================================
print("🎮 Inicializando sistema de pathfinding para Dofus Retro...")
mapa_dofus = MapaDofusRetro()
print("✅ Sistema listo - el mapa se escaneará automáticamente cuando sea necesario")
print("⚙️  IMPORTANTE: Si los clicks no son precisos, ajusta:")
print("   - region_mapa en MapaDofusRetro.__init__()")
print("   - ancho_celda y alto_celda en escanear_mapa_actual()")
# ============================================================================

if __name__ == "__main__":
 inicio = time.time()
 start_times = time.time()
 while True:
    if _bot_reiniciando:
        _bot_reiniciando = False
        inicio = time.time()
        print("↩️ Reinicio limpio — volviendo al inicio del loop principal")
        continue
    time.sleep(3)
    
    inventario()
    vent_pelea()
    recnec()    
    any_desk()
    recorrido=1
    ruta = 1
    controll = 1
    vuelta = 1
    ciclos =0000000
    vent_pelea()
    print("wile principal")
    print(f"vuelta vale {vuelta}")
    print(f"vuelta vale {vuelta}")
    #sala pelea minero
    
    
       
    sala()     
             
    if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5): 
        print("mina 1´pueblo detecta    1")
        while True:
            
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            if not heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and not heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
                break
            """any_desk()
            inter()
            pelear()
            recnec()
            ventana_nivel()
            inventario()
            print(f"vuelta vale {vuelta} pueblo")"""
            if vuelta >= ciclos:                
                print(f"vuelta vale {vuelta}")    
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    break
            
            
            
                
            
            #sala1    
            while heart.pixelMatchesColor(926,379, (180, 173, 143), tolerance=20) and heart.pixelMatchesColor(1134 , 346, (143, 113,  50), tolerance=20):      
                   
                
                

                vuelta = vuelta + 1
                
                if vuelta >= ciclos and heart.pixelMatchesColor(926,379, (180, 173, 143), tolerance=20) and heart.pixelMatchesColor(1134 , 346, (143, 113,  50), tolerance=20):                               
                    vuelta =0
                    recorrido=1    
                    minero(1)
                    
                    break

                print("en mina 1")
                inter()
                print(f" en la vuel ta {vuelta}")
                any_desk()
                inter()              
                ventana_nivel()     
                inventario() 
                
                    
               
    if heart.pixelMatchesColor(902,  758, (238, 254, 194), tolerance=10) and  heart.pixelMatchesColor(851, 759, (102,  50,   0), tolerance=20): 
        print("-2,4 mina 2")
        pelear2()
        if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
            print("mina 1´pueblo romper")
            break
        while True:
            pelear2()
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            if not heart.pixelMatchesColor(902,  758, (238, 254, 194), tolerance=10) and not  heart.pixelMatchesColor(851, 759, (102,  50,   0), tolerance=20):
                break
            if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
                break
            if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5): 
                print("mina 1´pueblo romper")
                break
            if heart.pixelMatchesColor(926,379, (180, 173, 143), tolerance=20) and heart.pixelMatchesColor(1134 , 346, (143, 113,  50), tolerance=20):
                break
            if heart.pixelMatchesColor(828 , 758 , (223, 220, 189), tolerance=20) and  heart.pixelMatchesColor(865,793,(201, 169, 132), tolerance=20):
                print("rompe en mina astrub identificada")
                break
            any_desk()
            inter()
            pelear2()
            recnec()
            ventana_nivel()
            inventario()
            print(f"vuelta vale {vuelta} -2,4 mina 2")
            if vuelta >= ciclos:                
                print(f"estoy en el wile principal de la salavuelta vale {vuelta}")    
                #no tocar
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    
                    break
            
            
            
                
            
            #sala1    
            while heart.pixelMatchesColor(573,  468, ( 92,  86,  67), tolerance=20) and heart.pixelMatchesColor(525,451,(228, 229, 213), tolerance=20):      
                   
                any_desk()
                inter() 
                posiciones_1 = [(532, 391), (875, 296), (942,  351), (976, 367), (1044,  383), (1077, 420), (1111,437), (840,  280), (787,  286)]
                inventario()
                
                vuelta = vuelta + 1
                if heart.pixelMatchesColor(1008 , 771 , ( 76,  98,  89), tolerance=15) and vuelta >= ciclos:
                    vuelta = 0
                    recorrido=1
                    ir_banco()
                    caminarMina()
                if vuelta >= ciclos and heart.pixelMatchesColor(573,  468, ( 92,  86,  67), tolerance=20) and heart.pixelMatchesColor(622,  384, ( 93,  84,  64), tolerance=20):                               
                    print("entra a hablar")    
                    vuelta = 0
                    recorrido=1
                    minero(2)
                    break

                print("en mina 1")
                inter()
                print(f" en la vuel ta {vuelta}")
                
                inter()              
                ventana_nivel()     
                any_desk()
                inventario()    
                
    #modificada                    
    """(900,  804,(104,  50,   1)"""                            
    if heart.pixelMatchesColor(900,  804,(104,  50,   1), tolerance=10) and  heart.pixelMatchesColor(863,  801, (143, 235,   0), tolerance=20): 
        pelear2()
        print("-2,-5 mina 3")
        if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
            print("mina 1´pueblo romper")
            break
        while True:
            pelear2()
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            if not heart.pixelMatchesColor(900,  804,(104,  50,   1), tolerance=10) and not heart.pixelMatchesColor(863,  801, (143, 235,   0), tolerance=20):
                break
            if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5): 
                print("mina 1´pueblo romper")
                break
            if heart.pixelMatchesColor(926,379, (180, 173, 143), tolerance=20) and heart.pixelMatchesColor(1134 , 346, (143, 113,  50), tolerance=20):
                break
            inter()
            pelear2()
            recnec()
            ventana_nivel()
            inventario()
            pelear2()
            print(f"vuelta vale {vuelta} -2,-5 mina 3")
            if 5 >= ciclos:                
                print(f"estoy en el wile principal de la salavuelta vale {vuelta}")    
                #no tocar
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    
                    break     
            
            
                
            
            #sala1    
            while heart.pixelMatchesColor(1045, 469, ( 92,  86,  62), tolerance=5) and heart.pixelMatchesColor(917, 384, ( 92,  84,  61), tolerance=5):      
                   
                
                posiciones_1 = [(1113, 385), (1079, 367), (1045, 350), (464, 333)]

                
                vuelta = vuelta + 1
                if heart.pixelMatchesColor(1008 , 771 , ( 76,  98,  89), tolerance=15) and vuelta >= ciclos:
                    vuelta = 0
                    recorrido=1
                    ir_banco()
                    caminarMina()
                if vuelta >= ciclos and heart.pixelMatchesColor(1045, 469, ( 92,  86,  62), tolerance=20) and heart.pixelMatchesColor(917, 384, ( 92,  84,  61), tolerance=20):                               
                    print("entra a hablar")   
                    vuelta = 0
                    recorrido=1 
                    minero(3)
                    break
               
                inter()
                print(f" en la vuel ta {vuelta}")
                
                inter()              
                ventana_nivel()     
                
                inventario()    
                

    if heart.pixelMatchesColor(846, 764,(203, 170, 130), tolerance=10) and  heart.pixelMatchesColor(870, 790 ,(230, 222, 199), tolerance=10): 
        pelear2()
        print("-3,9 mina 4")
        if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
            print("mina 1´pueblo romper, si entra aca rompe todo el ciclo en mina 4 detectando pueblo")
            break
        while True:
            pelear2()
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            if not heart.pixelMatchesColor(846, 764,(203, 170, 130), tolerance=10) and not heart.pixelMatchesColor(870, 790 ,(230, 222, 199), tolerance=10):
                break
            if heart.pixelMatchesColor(726 , 650,(122, 133,  74), tolerance=5) and  heart.pixelMatchesColor(719 ,  634, (223, 221, 200), tolerance=5): 
                print("mina 1´pueblo romper")
                break
            if heart.pixelMatchesColor(926,379, (180, 173, 143), tolerance=20) and heart.pixelMatchesColor(1134 , 346, (143, 113,  50), tolerance=20):
                break
            inter()
            pelear2()
            recnec()
            #ventana_nivel()
            inventario()
            print(f"vuelta vale {vuelta} -3,9 mina 4")
            
            if vuelta >= ciclos:                
                print(f"estoy en el wile principal de la salavuelta vale {vuelta}")    
                #no tocar
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    
                    break     
            
            
                
            
            #sala1    
            while heart.pixelMatchesColor(1001, 527, (206, 198, 144), tolerance=5) or heart.pixelMatchesColor(488, 420 , ( 93,  84,  64), tolerance=5):      
                   
                
                posiciones_1 = [(927, 371), (893,355), (859,337), (825, 321), (779, 273)]

                
                print(f" en la vuel ta {vuelta}")
                if heart.pixelMatchesColor(1008 , 771 , ( 76,  98,  89), tolerance=15) and vuelta >= ciclos:
                    vuelta = 0
                    recorrido=1
                    ir_banco()
                    caminarMina()
                if vuelta >= ciclos and heart.pixelMatchesColor(1001, 527, (206, 198, 144), tolerance=20) and heart.pixelMatchesColor(488, 420 , ( 93,  84,  64), tolerance=20):                               
                    print("entra a hablar")    
                    vuelta = 0
                    recorrido=1
                    minero(4)
                    break
               
                inter()
                print(f" en la vuel ta {vuelta}")
                
                inter()              
                #ventana_nivel()     
                
                inventario()    
                   
                                             
    if heart.pixelMatchesColor(828 , 758 , (223, 220, 189), tolerance=20) and  heart.pixelMatchesColor(865,793,(201, 169, 132), tolerance=20): 
        sala()
        pelear2()
        print("mina 5 ASTRUB")
        if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10):
                print("rompe mina mal identificada")
                continue
        while True:
            if heart.pixelMatchesColor(1184 , 635 , (176, 184, 147), tolerance=10) :
                break
            pelear2()
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5): 
                print("mina 1´pueblo romper")
                break
            if not heart.pixelMatchesColor(828 , 758 , (223, 220, 189), tolerance=20) and  not heart.pixelMatchesColor(865,793,(201, 169, 132), tolerance=20):
                break
            sala()
            if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) or heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5) :
                print("rompe mina mal identificada")
                break
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            inter()
            pelear2()
            recnec()
            #ventana_nivel()
            inventario()
            if heart.pixelMatchesColor(901,789 ,(210, 196, 107), tolerance=5) and  heart.pixelMatchesColor(848 ,775 ,(190, 152, 106), tolerance=5): 
                break
            print(f"vuelta vale {vuelta} 5 ASTRUB")
            if vuelta >= ciclos:                
                print(f"estoy en el wile principal de la salavuelta vale {vuelta}")    
                #no tocar
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    vuelta = 0
                    recorrido=1
                    break                                     

            #sala1    
            while heart.pixelMatchesColor(706,295, ( 92,  86,  64), tolerance=20) and heart.pixelMatchesColor(782, 284,( 93,  84,  64), tolerance=20):      
                   
                
                posiciones_1 = [(724,199), (927,267), (499,305), (532, 262), (635,210), (1007,213), (1211,281)]

                
                if heart.pixelMatchesColor(1008 , 771 , ( 76,  98,  89), tolerance=15) and vuelta >= ciclos:
                    vuelta = 0
                    recorrido=1
                    ir_banco()
                    caminarMina()
                if vuelta >= ciclos and heart.pixelMatchesColor(706,295, ( 92,  86,  64), tolerance=20) and heart.pixelMatchesColor(782, 284,( 93,  84,  64), tolerance=20):                               
                    print("entra a hablar")  
                    vuelta =0
                    recorrido=1  
                    minero(5)
                    
                    break

                print("en sala 1")
                inter()
                print(f" en la vuel ta {vuelta}")
                
                inter()              
                ventana_nivel()     
                inventario() 
                                    

    if heart.pixelMatchesColor(886 , 746 ,(200, 154,  67), tolerance=20) and  heart.pixelMatchesColor(864 , 792 , (181, 181, 175), tolerance=20): 
        print("mina 6 sufokia")
        pelear2()
        if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
            print("mina 1´pueblo romper")
            break
        while True:
            pelear2()
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            if not heart.pixelMatchesColor(886 , 746 ,(200, 154,  67), tolerance=20) and not heart.pixelMatchesColor(864 , 792 , (181, 181, 175), tolerance=20):
                break
            if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5): 
                print("mina 1´pueblo romper")
                break
            if heart.pixelMatchesColor(926,379, (180, 173, 143), tolerance=20) and heart.pixelMatchesColor(1134 , 346, (143, 113,  50), tolerance=20):
                break
            inter()
            pelear2()
            recnec()
            inventario()
            #ventana_nivel()
            if heart.pixelMatchesColor(1008 , 771 , ( 76,  98,  89), tolerance=15) and vuelta >= ciclos:
                    ir_banco()
                    caminarMina()
            print(f"vuelta vale {vuelta}  6 sufokia")
            if vuelta >= ciclos:                
                print(f"estoy en el wile principal de la salavuelta vale {vuelta}")    
                #no tocar
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    break                                     

            #sala1    
            while heart.pixelMatchesColor(731,486,(141, 114,  55), tolerance=5) and heart.pixelMatchesColor(756,493 ,(146, 110,  57), tolerance=5):      
                   
                
               
                if heart.pixelMatchesColor(1008 , 771 , ( 76,  98,  89), tolerance=15) and vuelta >= ciclos:
                    vuelta = 0
                    recorrido=1
                    ir_banco()
                    caminarMina()        
                vuelta = vuelta + 1
                if vuelta >= ciclos and heart.pixelMatchesColor(731,486,(141, 114,  55), tolerance=5) and heart.pixelMatchesColor(756,493 ,(146, 110,  57), tolerance=5):                               
                    print("entra a hablar")  
                    vuelta = 0
                    recorrido=1  
                    minero(6)
                    
                    break

                print("en sala 1")
                inter()
                print(f" en la vuel ta {vuelta}")
                
                inter()              
                ventana_nivel()     
                inventario() 
                              

    if heart.pixelMatchesColor(901,789 ,(210, 196, 107), tolerance=5) and  heart.pixelMatchesColor(848 ,775 ,(190, 152, 106), tolerance=5): 
        print("mina 7 rata brak")
        pelear2()
        if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
            print("mina 1´pueblo romper")
            break
        while True:
            pelear2()
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            if heart.pixelMatchesColor(828 , 758 , (223, 220, 189), tolerance=20) and  heart.pixelMatchesColor(865,793,(201, 169, 132), tolerance=20):
                break
            if not heart.pixelMatchesColor(901,789 ,(210, 196, 107), tolerance=5) and  not heart.pixelMatchesColor(848 ,775 ,(190, 152, 106), tolerance=5):
                break
            if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5): 
                print("mina 1´pueblo romper")
                break
            if heart.pixelMatchesColor(926,379, (180, 173, 143), tolerance=20) and heart.pixelMatchesColor(1134 , 346, (143, 113,  50), tolerance=20):
                break
            inter()
            pelear2()
            recnec()
            #ventana_nivel()
            inventario()
            print(f"vuelta vale {vuelta} 7 rata brak")
            if vuelta >= ciclos:                
                print(f"estoy en el wile principal de la salavuelta vale {vuelta}")    
                #no tocar
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    vuelta = 0
                    break                                     

            #sala1    
            while heart.pixelMatchesColor(1249,299, ( 46,  62,  49), tolerance=5) and heart.pixelMatchesColor(1114,296, ( 55,  51,  39), tolerance=5):      
                   
                
                posiciones_1 = [(669,366), (643,359), (364,522), (859,266), (895,249), (941,248), (973,235), (1007,193), (1076,168), (1098,181), (822,298), (922,246), (797,295), (736,331), (728,323), (618,402), (567,417), (532,434), (487,443), (453,458), (414, 505)]
                
                print(f" en la vuel ta {vuelta}")        
                vuelta = vuelta + 1
                if heart.pixelMatchesColor(1008 , 771 , ( 76,  98,  89), tolerance=15) and vuelta >= ciclos:
                    vuelta = 0
                    recorrido=1
                    ir_banco()
                    caminarMina()
                if vuelta >= ciclos and heart.pixelMatchesColor(1249,299, ( 46,  62,  49), tolerance=5) and heart.pixelMatchesColor(1114,296, ( 55,  51,  39), tolerance=5):                               
                    print("entra a hablar")    
                    vuelta = 0
                    recorrido=1
                    minero(7)
                    break

                print("en sala 1")
                inter()
                print(f" en la vuel ta {vuelta}")
                
                inter()              
                ventana_nivel()     
                inventario() 
                recorrido =1    
                            
                if recorrido ==1:
                    print("El número es impar. Ejecutando acción sube")
                    
                    
                    heart.click(341,678) 
                    heart.moveTo(150, 400)                    
                    
                    espera=0
                    while True: 
                        recnec() 
                        
                        inter() 
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break              
                        if heart.pixelMatchesColor(518, 446, (169, 125,  35), tolerance=5) and heart.pixelMatchesColor(606, 554, ( 50,  66,  52), tolerance=5):                                  
                                print("se detecta la sala 2")
                                print(f"reacorrido ahora vale {recorrido}")
                                break   

            #sala2    
            while heart.pixelMatchesColor(518, 446, (169, 125,  35), tolerance=5) and heart.pixelMatchesColor(606, 554, ( 50,  66,  52), tolerance=5):     
                   
                
                posiciones_2 = [(669,366), (643,359), (364,522), (760,317), (859,266), (895,249), (1043,208), (1117,162), (1038,230), (974,229), (940,247),(922 ,246), (821,297), (787,314), (728,323), (618,401), (592,391), (532,460), (483,470), (448,488), (414,504)]

                if minar_ws(posiciones_2, "m7_s2", "mina 7 rata brak"):
                    break
                
                

                print("en sala 2")
                inter()
                print(f" en la vuel ta {vuelta}")
                
                inter()              
                ventana_nivel()     
                inventario() 
                    
                            
                if recorrido ==1:
                    print("El número es impar. Ejecutando acción sube")
                    
                    
                    heart.click(339,679) 
                    heart.moveTo(150, 400)                    
                    
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break              
                        if heart.pixelMatchesColor(574,640,( 50,  66,  51), tolerance=5) and heart.pixelMatchesColor(549,619 , ( 36,  57,  47), tolerance=5):                                   
                                print("se detecta la sala 3")
                                
                            
                                print(f"reacorrido ahora vale {recorrido}")
                                break                    
                if recorrido ==2:
                    print("El número es impar. Ejecutando acción sube")
                    
                    
                    heart.click(1201,264) 
                    heart.moveTo(150, 400)                    
                    
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break              
                        if heart.pixelMatchesColor(1249,299, ( 46,  62,  49), tolerance=5) and heart.pixelMatchesColor(1114,296, ( 55,  51,  39), tolerance=5):                                  
                                print("se detecta la sala 1")
                                print(f"reacorrido ahora vale {recorrido}")
                                break     
            #sala3   
            while heart.pixelMatchesColor(574,640,( 50,  66,  51), tolerance=5) and heart.pixelMatchesColor(549,619 , ( 36,  57,  47), tolerance=5):       
                   
                
                posiciones_2 = [(813, 273), (457,459), (385,507), (854,290), (1096,147), (1008,201), (964,202), (922,244), (898,244), (786,314), (762,306),(712,341), (684,366), (618,402), (583,419), (415,505)]
                if minar_ws(posiciones_2, "m7_s3", "mina 7 rata brak"):
                    break
                        
                

                print("en sala 3")
                inter()
                print(f" en la vuel ta {vuelta}")
                
                inter()              
                ventana_nivel()     
                inventario() 
                    
                            
                if recorrido ==1:
                    print("El número es impar. Ejecutando acción sube")
                    
                    
                    heart.click(1201,263) 
                    heart.moveTo(150, 400)                    
                    
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break              
                        if heart.pixelMatchesColor(518, 446, (169, 125,  35), tolerance=5) and heart.pixelMatchesColor(606, 554, ( 50,  66,  52), tolerance=5):                                 
                                print("se detecta la sala 2")
                                
                                recorrido = 2
                                print(f"reacorrido ahora vale {recorrido}")
                                break                                        
   
   
    if heart.pixelMatchesColor(848,788 ,(169, 155, 139), tolerance=5) and  heart.pixelMatchesColor(892,785 ,(231, 220, 199), tolerance=5): 
        print("mina 8  brak abajo")
        pelear2()
        if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
            print("mina 1´pueblo romper")
            break
        while True:
            pelear2()
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            if not heart.pixelMatchesColor(848,788 ,(169, 155, 139), tolerance=5) and  not heart.pixelMatchesColor(892,785 ,(231, 220, 199), tolerance=5):
                break
            if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
                print("mina 1´pueblo romper")
                break
            if heart.pixelMatchesColor(926,379, (180, 173, 143), tolerance=20) and heart.pixelMatchesColor(1134 , 346, (143, 113,  50), tolerance=20):
                break
            inter()
            time.sleep(.5)
            pelear2()
            recnec()
            # refuerzo: si seguimos en pelea después de pelear2, reintentar
            if heart.pixelMatchesColor(1184, 635, (176, 184, 147), tolerance=10) or heart.pixelMatchesColor(1264, 622, (255, 33, 33), tolerance=10) or heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                print("[mina8 brak abajo] pelea persiste — pelear2 refuerzo")
                pelear2()
            #ventana_nivel()
            inventario()
            print(f"vuelta vale {vuelta} 8  brak abajo")
            if vuelta >= ciclos:                
                print(f"estoy en el wile principal de la salavuelta vale {vuelta}")    
                #no tocar
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    break                                     

            #sala1    
            while heart.pixelMatchesColor(817, 437,( 93,  84,  64), tolerance=5) and heart.pixelMatchesColor(782,454, ( 93,  84,  64), tolerance=5):      
                   
                
                
                
                        
                vuelta = vuelta + 1
                if heart.pixelMatchesColor(1008 , 771 , ( 76,  98,  89), tolerance=15) and vuelta >= ciclos:
                    vuelta = 0
                    recorrido=1
                    ir_banco()
                    caminarMina()
                if vuelta >= ciclos and heart.pixelMatchesColor(817, 437,( 93,  84,  64), tolerance=5) and heart.pixelMatchesColor(782,454, ( 93,  84,  64), tolerance=5):                               
                    print("entra a hablar")    
                    minero(8)
                    
                    recorrido=1
                    vuelta = 0
                    break

                print("en sala 1")
                inter()
                print(f" en la vuel ta {vuelta}")
                
                inter()              
                ventana_nivel()     
                inventario() 
                                         
                        
    if heart.pixelMatchesColor(335, 717, (127, 127, 127), tolerance=5) :
        pelear2()
        if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5):
            print("mina 1´pueblo romper")
            break
        while True:
            print(f"vuelta es {vuelta}")
            pelear2()
            if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
                break
            if not heart.pixelMatchesColor(335, 717, (127, 127, 127), tolerance=5) :
                break
            if heart.pixelMatchesColor(826,  781 ,(248, 218, 143), tolerance=5) and  heart.pixelMatchesColor(901 , 791, (253, 234, 189), tolerance=5): 
                print("mina 1´pueblo romper")
                break
            if heart.pixelMatchesColor(926,379, (180, 173, 143), tolerance=20) and heart.pixelMatchesColor(1134 , 346, (143, 113,  50), tolerance=20):
                break
            inter()
            pelear2()
            recnec()
            #ventana_nivel()
            inventario()
            print(f"vuelta vale {vuelta} ultima")
            if vuelta >= ciclos:                
                print(f"estoy en el wile principal de la salavuelta vale {vuelta}")    
                #no tocar
                if heart.pixelMatchesColor(809,  416, ( 92,  86,  66), tolerance=10) and heart.pixelMatchesColor(885,  288, (147, 109,  45), tolerance=10) :
                    vuelta = 0
                    break
        #mina 1
            while heart.pixelMatchesColor(656,  481, (191, 184, 153), tolerance=20) and heart.pixelMatchesColor(894, 428, (191, 184, 153), tolerance=20):         
                print(f"vuelta vale {vuelta} ultima")        
                inter()
                print("en mina 111111111")
                posiciones_1 = [
            (622, 183), (656,  200), (690,  217), (724, 234), (766, 271),
            (824, 286), (893, 321), (960,  355), (983,  342), (1028, 389),
            (1061,  406), (1177,  452), (1231,  493), (1265, 510)
        ]
                
                
                inventario()
                if minar_ws(posiciones_1, "m9_s1", "mina 9"):
                    break
                inter()
                ventana_nivel()
                print(f"recorrido es {recorrido}")
                if recorrido ==2:
                    recorrido=1
                if recorrido ==3:
                    recorrido=1           
                if recorrido ==1:
                    print("El número es impar. Ejecutando acción sube")
                    
                    
                    heart.click(1266, 678) 
                    heart.moveTo(150, 400)
                    
                    #el if detecta si aun esta en la sala 1   
                    #if heart.pixelMatchesColor(1133, 347, (145, 111,  55), tolerance=20) and heart.pixelMatchesColor(1129,  237, (113,  83,  36), tolerance=20): 
                    
                    #el while espera a que se renderice la sala siguiente
                    espera=0
                    while True: 
                        recnec() 
                        
                        inter() 
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break              
                        if heart.pixelMatchesColor(1262,  494, (171, 136,  72), tolerance=20) and heart.pixelMatchesColor(338 , 215, (177, 136,  79), tolerance=20):                                   
                                print("se detecta la sala 2")
                                print(f"reacorrido ahora vale {recorrido}")
                                break       
            #sala2
            while heart.pixelMatchesColor(1262,  494, (171, 136,  72), tolerance=20) and heart.pixelMatchesColor(338 , 215, (177, 136,  79), tolerance=20):      
                #inventario(recorrido=None)
                print("en mina 2")
                print(f"vuelta vale {vuelta} ultima")
                posiciones_2 = [
            (521, 165), (622, 183), (656, 200), (669, 213), (745,  221),
            (847,  273), (880, 290), (940, 360), (1028, 389), (1130, 441),
            (1151,  428), (1219, 462)]
                
                if minar_ws(posiciones_2, "m9_s2", "mina 9"):
                    break

                inter()
                inventario()
                print(f"recorrido es {recorrido}")        #
                ventana_nivel()                           
                if recorrido ==1:
                    
                    print("El número es impar. Ejecutando acción sube")
                    
                    heart.click(1264, 680) 
                    heart.moveTo(150, 400)
                    #el if detecta si aun esta en la sala 2   
                    
                            
                            #el while espera a que se renderice la sala siguiente
                    espera=0
                    while True:
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                                        
                        if heart.pixelMatchesColor(587, 518, (178, 172, 143), tolerance=10) and heart.pixelMatchesColor(757,  465 , (185, 178, 148), tolerance=10):                                   
                            print("se detecta la sala 3")
                            print(f"reacorrido ahora vale {recorrido}")
                            break
                
                if recorrido ==2:
                    print("El número es par. Ejecutando acción Baja") 
                    
                    heart.click(338, 195)       
                    heart.moveTo(150, 400)
                                    
                            #el while espera a que se renderice la sala siguiente
                    espera=0
                    while True:
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break
                        #esperando sala 1
                        if heart.pixelMatchesColor(656,  481, (191, 184, 153), tolerance=20) and heart.pixelMatchesColor(894, 428, (191, 184, 153), tolerance=20):                                
                            print("se detecta la sala 1")
                            break                    
            #sala3
            while heart.pixelMatchesColor(587, 518, (178, 172, 143), tolerance=10) and heart.pixelMatchesColor(757,  465 , (185, 178, 148), tolerance=10):
                print("en mina 3")
                print(f"vuelta vale {vuelta} ultima")
                posiciones_3 = [(483,  165),(494, 163),(549, 199), (562, 199), (596,  216), (779, 267),(650,  250),(685,  268), (831,  247),
                (864 ,  228), (899, 211),(932,  194), (967,  177), (1000, 159), (1024, 149),
                (1221, 505),(1192, 527), (1153, 470), (1125, 493),(1071, 458),(1057 ,  457), (1023,  440),
                (364,  487), (417, 477), (432,  452), (465, 435), (499, 417), (533 ,  420), (567,  383)]
                
                if minar_ws(posiciones_3, "m9_s3", "mina 9"):
                    break
                inter()
                inventario()
                                    
                
                if recorrido ==1:
                    
                    print("El número es impar. Ejecutando acción sube")        
                    time.sleep(1)
                    heart.click((1210, 676))
                    heart.moveTo(150, 400)
                    #el if detecta si aun esta en la sala 3   
                    
                            
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(746, 334, ( 92,  84,  61), tolerance=10) and heart.pixelMatchesColor(991,  388, (203, 158,  30), tolerance=10):                                  
                                print("se detecta la sala 4")
                                print(f"reacorrido ahora vale {recorrido}")
                                break 
                
                if recorrido ==2:
                    
                    print("El número es par. Ejecutando acción Baja")
                    time.sleep(1)
                    heart.click(338, 194)
                    heart.moveTo(150,400)   
                    #detecta si aun sigue en la sala 3
                    
                            
                            #el while espera a que se renderice la sala anterior
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        
                        if heart.pixelMatchesColor(1262,  494, (171, 136,  72), tolerance=20) and heart.pixelMatchesColor(338 , 215, (177, 136,  79), tolerance=20):                                
                                print("se detecta la sala 2")
                                break   
                if recorrido ==3:
                    
                    print("El número es impar. Ejecutando acción sube")        
                    time.sleep(1)
                    heart.click((1236,  180))
                    heart.moveTo(150, 400)
                    recorrido = 1              
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(679, 541, ( 92,  84,  61), tolerance=10) and heart.pixelMatchesColor(877, 453, ( 92,  84,  61), tolerance=10):                                  
                                print("se detecta la sala 4")
                                print(f"reacorrido ahora vale {recorrido}")
                                break
                if recorrido ==4:
                    time.sleep(1)
                    print("El número es impar. Ejecutando acción sube")        
                    recorrido = 2
                    heart.click((1210, 676))
                    heart.moveTo(150, 400)
                    #el if detecta si aun esta en la sala 3   
                    
                            
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(746, 334, ( 92,  84,  61), tolerance=10) and heart.pixelMatchesColor(991,  388, (203, 158,  30), tolerance=10):                                  
                                print("se detecta la sala 4")
                                print(f"reacorrido ahora vale {recorrido}")
                                break        
                                
            #sala4
            while heart.pixelMatchesColor(746, 334, ( 92,  84,  61), tolerance=10) and heart.pixelMatchesColor(991,  388, (203, 158,  30), tolerance=10):
                print("en mina 4474")
                print(f"vuelta vale {vuelta} ultima")
                posiciones_4= [
            (523, 165), (658,  201), (726,  235), (760,  252), (859,  303),
            (897, 272), (942,  357), (1085 ,394), (1119, 411), (1152, 428),
            (1236, 444), (1253, 480)]
                minar(posiciones_4)
                
                inter()                
                inventario()           
                print(f"recorrido es {recorrido}")                    
                ventana_nivel() 
                if recorrido ==1:
                    recorrido = 3
                    print("El número es impar. Ejecutando acción sube")        
                    time.sleep(1)
                    heart.click(343, 193)
                    heart.moveTo(150, 400)
                    #el if detecta si aun esta en la sala 3   
                    
                            
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(587, 518, (178, 172, 143), tolerance=10) and heart.pixelMatchesColor(757,  465 , (185, 178, 148), tolerance=10):                                  
                                print("se detecta la sala 3")
                                print(f"reacorrido ahora vale {recorrido}")
                                break 
                if recorrido ==2:
                    time.sleep(1)
                    print("El número es impar. Ejecutando acción sube")        
                    
                    heart.click(343, 193)
                    heart.moveTo(150, 400)
                    #el if detecta si aun esta en la sala 3   
                    
                            
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(587, 518, (178, 172, 143), tolerance=10) and heart.pixelMatchesColor(757,  465 , (185, 178, 148), tolerance=10):                                  
                                print("se detecta la sala 3")
                                print(f"reacorrido ahora vale {recorrido}")
                                break        
                
                                
                

            #sala5
            while heart.pixelMatchesColor(679, 541, ( 92,  84,  61), tolerance=10) and heart.pixelMatchesColor(877, 453, ( 92,  84,  61), tolerance=10):
                print("en mina 5") 
                print(f"vuelta vale {vuelta} ultima")
                posiciones_5 = [
            (399, 500), (469,  502), (532,   460), (567,  417), (602, 400),
            (703,  348), (737, 328), (804,  293), (862, 254), (983, 203),
            (1007, 189), (1042, 172), (1108,  166)]
                minar(posiciones_5)
                inter()                
                inventario()            
                print(f"recorrido es {recorrido}")                    
                ventana_nivel() 
                if recorrido ==1:
                    time.sleep(1)
                    print("El número es impar. Ejecutando acción sube")        
                    
                    heart.click(1271, 195)
                    heart.moveTo(150, 400)
                    #el if detecta si aun esta en la sala 3   
                    
                            
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(782, 328, (119, 112,  81), tolerance=20) and heart.pixelMatchesColor(1241, 193, (147, 106,  47), tolerance=20):                                  
                                print("se detecta la sala 6")
                                print(f"reacorrido ahora vale {recorrido}")
                                break 
                
                if recorrido ==2:
                    
                    print("El número es par. Ejecutando acción Baja")
                    time.sleep(1)
                    heart.click(337, 678)
                    heart.moveTo(150, 400)   
                                
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        
                        if heart.pixelMatchesColor(587, 518, (178, 172, 143), tolerance=10) and heart.pixelMatchesColor(757,  465 , (185, 178, 148), tolerance=10):                                
                                print("se detecta la sala 3")
                                recorrido = 4
                                break 
                
                    
                    
                            
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(587, 518, (178, 172, 143), tolerance=10) and heart.pixelMatchesColor(757,  465 , (185, 178, 148), tolerance=10):                                  
                                print("se detecta la sala 3")
                                
                                break  
                        
            #sala 6            
            while heart.pixelMatchesColor(782, 328, (119, 112,  81), tolerance=20) and heart.pixelMatchesColor(1241, 193, (147, 106,  47), tolerance=20):
                print("en mina 6") 
                print(f"vuelta vale {vuelta} ultima")
                posiciones_6 = [(494, 163), (562, 199), (596,  216), (779, 267), (831,  247),
            (864 ,  228), (899, 211),(932,  194), (967,  177), (1000, 159), (1024, 149),
            (1221, 505), (1153, 470), (1071, 458),
            #bronce abajo derecha#
            (1192, 527), (1125, 493), (1057 ,  457), (1023,  440),
            #bronce abajo izquierda
            (364,  487), (417, 477), (432,  452), (465, 435), (499, 417), (533 ,  420), (567,  383),
            #bronce arriba derecha
            (482, 164), (570, 176), (650,  250), (685,  268)]
                
                minar(posiciones_6)
                inter()                
                inventario() 
                            
                                
                print(f"recorrido es {recorrido}")                    
                ventana_nivel() 
                if recorrido ==1:
                    
                    print("El número es impar. Ejecutando acción sube")        
                    time.sleep(1)
                    heart.click(341,  197)
                    heart.moveTo(150, 400)      
                            
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(583, 177, (203, 158,  30), tolerance=10) and heart.pixelMatchesColor(1058,  420, (203, 158,  30), tolerance=10):                                  
                                print("se detecta la sala 7")
                                
                                print(f"reacorrido ahora vale {recorrido}")
                                break 
                
                if recorrido ==2:
                    time.sleep(1)
                    print("El número es par. Ejecutando acción Baja")
                    
                    heart.click(363, 691)
                    heart.moveTo(150,400)   
                    
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        #esperando sala 5
                        if heart.pixelMatchesColor(679, 541, ( 92,  84,  61), tolerance=10) and heart.pixelMatchesColor(877, 453, ( 92,  84,  61), tolerance=10):                                
                                print("se detecta la sala 2")
                                break 
                        
            #sala7                    
            while heart.pixelMatchesColor(800, 286, (147, 108,  48), tolerance=20) and heart.pixelMatchesColor(715 ,240, (147, 109,  45), tolerance=20):
                print("en mina 7")
                print(f"vuelta vale {vuelta} ultima")
                posiciones_7 = [
            (1199, 475), (1143,  436), (937,  332), (871, 295), (837,  279),
            (691,  166), (633, 176)]
                print(vuelta, ciclos)
                
                
                if heart.pixelMatchesColor(1008 , 771 , ( 76,  98,  89), tolerance=15) and vuelta >= ciclos:
                    vuelta = 0
                    recorrido=1
                    ir_banco()
                    caminarMina()
                if vuelta >= ciclos and heart.pixelMatchesColor(800, 286, (147, 108,  48), tolerance=20) and heart.pixelMatchesColor(715 ,240, (147, 109,  45), tolerance=20):                              
                    print("entra a hablar")   
                    vuelta = 0
                    recorrido=1 
                    minero(9)
                    

                    break
                print(vuelta, ciclos)
                inter()                
                inventario() 
                        
                                
                print(f"recorrido es {recorrido}")                    
                ventana_nivel() 
                if recorrido ==1:
                    
                    print("El número es impar. Ejecutando acción sube")        
                    
                    heart.click(339,198)
                    heart.moveTo(150, 400)           
                            
                    espera=0
                    while True: 
                        recnec() 
                        
                        inter() 
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(338,  193, (164, 123,  37), tolerance=10) and heart.pixelMatchesColor(344, 209, (150, 101,  40), tolerance=10):                                  
                                print("se detecta la sala 8")
                                
                                print(f"reacorrido ahora vale {recorrido}")
                                break 
                
                if recorrido ==2:
                    
                    print("El número es par. Ejecutando acción Baja")
                    
                    heart.click(1270, 680)
                    heart.moveTo(150,400)   
                    
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        #esperando sala 6
                        if heart.pixelMatchesColor(782, 328, (119, 112,  81), tolerance=20) and heart.pixelMatchesColor(1241, 193, (147, 106,  47), tolerance=20):                                
                                print("se detecta la sala 6")
                                break 
            #sala8                    
            while heart.pixelMatchesColor(338,  193, (164, 123,  37), tolerance=10) and heart.pixelMatchesColor(344, 209, (150, 101,  40), tolerance=10):
                print("en mina 8")
                print(f"vuelta vale {vuelta} ultima")
                posiciones_8 = [
            (611, 152), (658, 200), (726,  234), (758,  252), (793,  269),
            (995, 372), (1063, 407), (1096,  424), (1164, 459), (1198,  476)]
                
                minar(posiciones_8)
                inter()                
                inventario() 
                vuelta = vuelta + 1                
                print(f"recorrido es {recorrido}")                   
                ventana_nivel() 
                if recorrido ==1 or recorrido ==2:
                    #vuelta = vuelta +1
                    print("El número es par. Ejecutando acción baja")        
                    
                    heart.click((1268, 678))
                    heart.moveTo(150, 400)
                    recorrido = 2   
                    
                            
                    espera=0
                    while True:  
                        recnec() 
                        
                        inter()
                        espera += 1
                        time.sleep(.2)                
                        if espera == 80:
                            break                   
                        if heart.pixelMatchesColor(800, 286, (147, 108,  48), tolerance=20) and heart.pixelMatchesColor(715 ,240, (147, 109,  45), tolerance=20):                                  
                                print("se detecta la sala 7")
                                
                                
                                break                    
    time.sleep(3)
    if heart.pixelMatchesColor(852, 817 , (255, 142,   0), tolerance=5) :   
        print("entra a pelea de afuera")
        pelear2()                         
    if heart.pixelMatchesColor(718, 634, (223, 221, 199), tolerance=10):
        vuelta = 0
        caminarMina()
    
    tiempo_transcurrido = time.time() - inicio
    if tiempo_transcurrido >= TIEMPO_LIMITE:
        print(f"Tiempo límite alcanzado. Reiniciando juego...")
        reiniciar_juego()
        inicio = time.time()



import cv2 
import time
import numpy as np
import pyautogui
import pyautogui as heart
import os
def recnec():
    if heart.pixelMatchesColor(772, 546, (255,  97,   0), tolerance=15) or heart.pixelMatchesColor(655,448,(220, 129,   0), tolerance=15) or heart.pixelMatchesColor(767 , 527 , (255,  97,   0), tolerance=15)  or heart.pixelMatchesColor(766, 556 , (255,  97,   0), tolerance=15) or heart.pixelMatchesColor(848, 560,(250,  95,   0), tolerance=15):
        print("entra a reconectar")
        while True:    
            print("enrta al wile")
            if  heart.pixelMatchesColor(772, 546, (255,  97,   0), tolerance=15) or heart.pixelMatchesColor(655,448,(220, 129,   0), tolerance=15) or heart.pixelMatchesColor(767 , 527 , (255,  97,   0), tolerance=15) :
                print("encontrada")
                heart.click(767 , 527)
                time.sleep(1)
                heart.click(772, 547)
                time.sleep(1)
                heart.click(655, 448)
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
                        
           

            if  heart.pixelMatchesColor(864, 727, (216,   1,   1), tolerance=15):
                    time.sleep(5)
                    break
    return
def ir_banco():
    
   
    while True:
        recnec()
        heart.click(670, 536)
        time.sleep(5)
        
        while heart.pixelMatchesColor(747, 438, (172, 162, 122), tolerance=15) and heart.pixelMatchesColor(755, 462 , (159, 146, 105), tolerance=15):
            print("detecta taller afuera")
            
            cuenta = 0 
            while True:
                cuenta = cuenta + 1
                if cuenta == 10:
                    break
                print("inicia zapi")    
                
                heart.click(839,385)                                 
                time.sleep(.2)           
                    
                heart.click(890 , 421)

                
                while True:
                    if heart.pixelMatchesColor(886 , 190 , (255, 255, 255), tolerance=15) and heart.pixelMatchesColor( 1048 ,  365 , (255, 255, 255), tolerance=15):
                        time.sleep(.3)
                        heart.click(656, 241)                                 
                        time.sleep(.5)
                        heart.click(693, 331)
                        while True:
                            if heart.pixelMatchesColor(798,  297, (131, 124,  75), tolerance=15) and heart.pixelMatchesColor(1005, 342,  (133, 123,  90), tolerance=15):
                                break
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
                time.sleep(0.2)
                cuenta = cuenta + 1
                if cuenta == 50:
                    break
                if heart.pixelMatchesColor(1065,  288 , (170, 158, 132), tolerance=15) and heart.pixelMatchesColor(780,  163,  (130, 129,  34), tolerance=15):
                    break       
            break        
              
        while heart.pixelMatchesColor(1065,  288 , (170, 158, 132), tolerance=15) and heart.pixelMatchesColor(780,  163,  (130, 129,  34), tolerance=15):                     
                

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
            cuenta = 0  
            while True:
                time.sleep(0.2)
                cuenta = cuenta + 1
                if cuenta == 300:
                    break
                if heart.pixelMatchesColor(602, 337 , (255, 255, 206), tolerance=15):         
                      
                    time.sleep(.2)      
                    heart.click(666, 453)
                    time.sleep(.2) 


                """"""        
                if heart.pixelMatchesColor(1142, 262 , ( 81,  74,  60), tolerance=15):   
                    #clic recursos
                    time.sleep(1.5)
                    heart.moveTo(426,  296)   
                    time.sleep(.2)      
                    heart.click()

                    


                    #mover mineral bakelita
                    time.sleep(.5)
                    heart.moveTo(461,411)                       
                    heart.mouseDown()
                    time.sleep(.3)
                    heart.moveTo(1087, 530)
                    heart.mouseUp()
                    time.sleep(.3)
                    heart.write("100", interval=0.4)
                    time.sleep(.3)
                    heart.press("enter")
                    time.sleep(.3)
                    #mover mineral bronce
                    time.sleep(1)
                    heart.moveTo(371,365)   
                    heart.mouseDown()
                    heart.moveTo(1087, 530)
                    time.sleep(.3)
                    heart.mouseUp()
                    time.sleep(.3)
                    heart.write("300", interval=0.4)
                    time.sleep(.3)
                    heart.press("enter")
                    time.sleep(.3)
                    #mover mineral oro
                    time.sleep(1)
                    heart.moveTo(373,607)   
                    heart.mouseDown()
                    time.sleep(.3)
                    heart.moveTo(1087, 530)
                    time.sleep(.3)
                    heart.mouseUp()
                    time.sleep(.3)
                    heart.write("600", interval=0.4)
                    time.sleep(.3)
                    heart.press("enter")
                    time.sleep(.3)
                    #mover mineral plata
                    time.sleep(1)
                    heart.moveTo(495,567)   
                    heart.mouseDown()
                    heart.moveTo(1087, 530)
                    heart.mouseUp()
                    time.sleep(.3)
                    heart.write("200", interval=0.4)
                    time.sleep(.3)
                    heart.press("enter")
                    time.sleep(.3)

                    heart.click(1249, 264)
                    time.sleep(1)
                    heart.click(534 , 569)
                    #caminarMina()
                    while True:
                        if heart.pixelMatchesColor(798,  297, (131, 124,  75), tolerance=15) and heart.pixelMatchesColor(1005, 342,  (133, 123,  90), tolerance=15):
                            print("romple saliendo del banco")
                            break   
                    break
            #camino taller        
            while heart.pixelMatchesColor(798,  297, (131, 124,  75), tolerance=15) and heart.pixelMatchesColor(1005, 342,  (133, 123,  90), tolerance=15):
                
                
                    
                cuenta = 0 
                while True:
                    cuenta = cuenta + 1
                    if cuenta == 10:
                        break
                    print("inicia zapi")    
                    
                    heart.click(997 ,369)
                    time.sleep(.3)
                    heart.click(1063, 407)

                    
                    while True:
                        if heart.pixelMatchesColor(886 , 190 , (255, 255, 255), tolerance=15) and heart.pixelMatchesColor( 1048 ,  365 , (255, 255, 255), tolerance=15):
                            time.sleep(.3)
                            heart.click(710 ,455)                                 
                            
                            while True:
                                if heart.pixelMatchesColor(747, 438, (172, 162, 122), tolerance=15) and heart.pixelMatchesColor(755, 462 , (159, 146, 105), tolerance=15):
                                    heart.click(1084 ,350)
                                    while True:

                                        if heart.pixelMatchesColor(840 , 232, (164, 154,  51), tolerance=15) and heart.pixelMatchesColor( 839, 280 , (164, 154,  51), tolerance=15):
                                            print("llego al taller 1")    
                                            break
                                    break
                            break
                    break
                   
        print("llego al taller")
        break  
def similitud_imagen_en_pantalla_anilli(imagen, region_busqueda):
    if not os.path.exists(imagen):
        print(f"Error: El archivo {imagen} no existe.")
        return 0

    template = cv2.imread(imagen, cv2.IMREAD_COLOR)
    if template is None:
        print(f"Error: No se pudo cargar la imagen {imagen}")
        return 0

    screenshot = pyautogui.screenshot(region=region_busqueda)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    return max_val 
def similitud_imagen_en_pantalla(imagen, region_busqueda=(0, 360, 323, 441)):
    if not os.path.exists(imagen):
        print(f"Error: El archivo {imagen} no existe.")
        return 0

    template = cv2.imread(imagen, cv2.IMREAD_COLOR)
    if template is None:
        print(f"Error: No se pudo cargar la imagen {imagen}")
        return 0

    screenshot = pyautogui.screenshot(region=region_busqueda)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    return max_val       
def hacer_anillos():
    heart.click(970 ,420)
    time.sleep(.4)
    heart.click(1074 ,483)
    while True:
        if heart.pixelMatchesColor(1237,224, ( 81,  74,  60), tolerance=15) and heart.pixelMatchesColor( 1205 ,  309 ,( 81,  74,  60), tolerance=15):
            #bakelita
            heart.moveTo(881 , 420)
            heart.mouseDown()
            time.sleep(.2)
            heart.moveTo(1031,606)
            heart.mouseUp()
            time.sleep(.2)
            heart.write("2")
            time.sleep(.4)
            heart.press("enter")
            #bronce
            heart.moveTo( 922,416)
            heart.mouseDown()
            heart.moveTo(1074 , 603)
            time.sleep(.2)
            heart.mouseUp()
            time.sleep(.2)
            heart.write("6")
            time.sleep(.4)
            heart.press("enter")
            #bronce
            heart.moveTo(964 ,422)
            heart.mouseDown()
            heart.moveTo(1125 ,603 )
            time.sleep(.2)
            heart.mouseUp()
            time.sleep(.2)
            heart.write("3")
            time.sleep(.4)
            heart.press("enter")
            #oro
            heart.moveTo(1007 ,415)
            heart.mouseDown()
            heart.moveTo(1170 , 604 )
            time.sleep(.2)
            heart.mouseUp()
            time.sleep(.2)
            heart.write("1")
            time.sleep(.4)
            heart.press("enter")

            time.sleep(1)
            heart.click(1040,653)
            time.sleep(.2)
            heart.write("100")
            time.sleep(.4)
            heart.press("enter")

            heart.click(1187 ,649)
            time.sleep(5)
            if not heart.pixelMatchesColor(1237,224, ( 81,  74,  60), tolerance=15) and not heart.pixelMatchesColor( 1205 ,  309 ,( 81,  74,  60), tolerance=15):
                heart.click(970 ,420)
                time.sleep(.4)
                heart.click(1074 ,483)
            while True:
                similitud = similitud_imagen_en_pantalla("termino.png")

                print(f"Similitud detectada: {similitud:.3f}")

                if similitud >= 0.9:  # Umbral configurable
                    print("¡Imagen detectada! Terminando el bucle.")
                    break

                time.sleep(0.5)
            while True:
                time.sleep(.3)
                if heart.pixelMatchesColor(845 , 452, (255,  97,   0), tolerance=15):
                    heart.click(850 , 452)
                if heart.pixelMatchesColor(853 , 441 , (255, 255, 255), tolerance=15):
                    heart.click(1243 ,309)
                    break   
            break         
def vender():
    var = 0
    while True:    
        """heart.click(807 , 308)
        time.sleep(0.2)
        heart.click(873, 322)
        time.sleep(2)"""
        recnec()
        if var == 1:
            
            break
        print(f"wile princ {var}")
        while True:
            if not heart.pixelMatchesColor(1271,  451 , (255, 255, 255), tolerance=15) and not heart.pixelMatchesColor(1167, 314 , (255, 255, 255), tolerance=15):
                heart.click(807 , 308)
                time.sleep(0.2)
                heart.click(873, 322)
                time.sleep(2)
                print("entra aca")
                if not heart.pixelMatchesColor(1028, 444 ,(252, 245, 233), tolerance=15) or not heart.pixelMatchesColor(1028, 444 ,(252, 245, 233), tolerance=15):
                    print("deja de cdnder 1")
                    heart.click(1255, 328)
                    time.sleep(5)
                    var = 1
                    break
            recnec()    
            if heart.pixelMatchesColor(1028 , 420 ,(252, 245, 233), tolerance=15) and heart.pixelMatchesColor(1039 , 423 , (222, 219, 183), tolerance=15) and heart.pixelMatchesColor(1027 ,  445, (237, 232, 208), tolerance=15) :  # Umbral configurable
                print("¡Imagen detectada! Terminando el bucle.1")
                #time.sleep(.5)
                heart.click(1028 , 420)
                time.sleep(.1)
                heart.moveTo(400,150)
                heart.press("enter")
                time.sleep(.1)
                heart.press("enter")
                time.sleep(.1)
                if not heart.pixelMatchesColor(1028, 444 ,(252, 245, 233), tolerance=15) or not heart.pixelMatchesColor(1028, 444 ,(252, 245, 233), tolerance=15):
                    print("deja de cdnder 2")
                    heart.click(1255, 328)
                    time.sleep(3)
                    var = 1
                    break
            time.sleep(1)    
            if heart.pixelMatchesColor(1027 ,  445, (237, 232, 208), tolerance=15) and heart.pixelMatchesColor(1039 ,  449 ,(222, 219, 183), tolerance=15):  # Umbral configurable
                print("¡Imagen detectada! Terminando el bucle.2")
                #time.sleep(.5)
                heart.click(1197 ,  449)
                time.sleep(.1)
                heart.moveTo(40,150)
                heart.press("enter")
                time.sleep(.1)
                heart.press("enter")
                time.sleep(.1)
                if not heart.pixelMatchesColor(1028, 444 ,(252, 245, 233), tolerance=15) or not heart.pixelMatchesColor(1028, 444 ,(252, 245, 233), tolerance=15):
                    print("deja de cdnder 3")
                    heart.click(1255, 328)
                    time.sleep(3)
                    var = 1
                    break                
            
            if not heart.pixelMatchesColor(1028, 444 ,(252, 245, 233), tolerance=15) or not heart.pixelMatchesColor(1028, 444 ,(252, 245, 233), tolerance=15):
                if var == 1:
            
                    break
                
                print("deja de cdnder")
                heart.click(1255, 328)
                time.sleep(3)
                recnec()
                break
            if var == 1:
            
                break
    time.sleep(3)            


def sacar_recurso():
    time.sleep(.5)
    if  heart.pixelMatchesColor( 441,334 ,(129, 128,  33), tolerance=15):
        "recinto banco, dar clicl en buho"
        time.sleep(1)
        heart.click(941,284)
        time.sleep(.5)
        heart.click(973,297)

        while True:
            time.sleep(2)
            recnec()
            if not heart.pixelMatchesColor( 441,334 ,(129, 128,  33), tolerance=15) and heart.pixelMatchesColor(755, 462 , (159, 146, 105), tolerance=5):
                print("dar clicl en buho")
                time.sleep(1)
                heart.click(941,284)
                time.sleep(.5)
                heart.click(973,297)
               
            if heart.pixelMatchesColor(376,250,(255, 208, 102), tolerance=15):
                print("detectar ventana del buho ") 
                time.sleep(.5)
                heart.click(421,458)
                time.sleep(.5)
            print("ventana de banco--> dar cliclc pestaña recurso")    
            if heart.pixelMatchesColor(376,250,(255, 208, 102), tolerance=15) :
                "recurso bancoi"
                time.sleep(2)
                heart.click(426,299)
                time.sleep(.5)

                "pestaña recurso inventario"
                heart.click(1098, 300)
                time.sleep(.5)



                while True:
                    time.sleep(.5)
                    print("intentando pasar el recurso")
                    "recurso detectado"
                    
                    
                    recnec()
                    if not heart.pixelMatchesColor(1226,249 , (255, 255, 255), tolerance=5) :
                        print("entra al wile a pasar las cosas")
                        time.sleep(10)
                        recnec()
                        print("entra a cerrar si no detecta la ventana se recurso")
                        break
                    " ver que esta en pestaña recurso y pasar el recurso"
                    if heart.pixelMatchesColor(424,291,( 81,  74,  60), tolerance=15) :
                        time.sleep(1)
                        print("buscar el recurso y pasarlo al inventario")
                        time.sleep(.5)
                        heart.moveTo(376,369)                       
                        heart.mouseDown()
                        time.sleep(.3)
                        heart.moveTo(1228,416)
                        heart.mouseUp()
                        time.sleep(.3)
                        heart.write("800", interval=0.4)
                        time.sleep(.3)
                        heart.press("enter")
                        time.sleep(.3)
                        break
                if not heart.pixelMatchesColor(1053,369 ,(190, 185, 152), tolerance=5) or not  heart.pixelMatchesColor(1044,367 ,(190, 185, 152), tolerance=5) or not heart.pixelMatchesColor(1054,357 ,(190, 185, 152), tolerance=5) or not heart.pixelMatchesColor(1066,368 ,(190, 185, 152), tolerance=5) or not heart.pixelMatchesColor(1053,377 ,(190, 185, 152), tolerance=5):
                    heart.click(1250,263)
                    time.sleep(.5)
                    print("hay un recurso en inventario")
                    break        
    intercambio()                
def intercambio():

    while True:
        #arriba
        heart.click(1261,264)
        time.sleep(1)
        heart.click(1178,470)
        time.sleep(.5)
        #abajo
        #heart.click(1257,302)
        time.sleep(1)
        heart.click(1217,497)
        time.sleep(.5)
        
        if   heart.pixelMatchesColor(1017, 414,(255, 255, 255), tolerance=15):
            break

    while True:
        if   heart.pixelMatchesColor(1209,225, (255, 255, 255), tolerance=15):
            time.sleep(1)
            heart.click(930,271)
            time.sleep(1)

            #pasar el recurso
            heart.moveTo(885,346)
            time.sleep(.5)
            heart.keyDown("ctrl")
            heart.click(clicks=2,interval=.2)
            heart.keyUp("ctrl")
            while True:
                print("esperando para aceptar")
                if   heart.pixelMatchesColor(1233, 654 ,(255,  97,   0), tolerance=15):
                    heart.click(1138,654)
                time.sleep(.5)
                if not heart.pixelMatchesColor(1200,223 , (255, 255, 255), tolerance=15):
                    break

def meter_recurso():
    time.sleep(.5)
    if  heart.pixelMatchesColor( 441,334 ,(129, 128,  33), tolerance=15):
        "recinto banco, dar clicl en buho"
        time.sleep(1)
        heart.click(941,284)
        time.sleep(.5)
        heart.click(973,297)

        while True:
            time.sleep(2)
            recnec()
            if not heart.pixelMatchesColor( 441,334 ,(129, 128,  33), tolerance=15) and heart.pixelMatchesColor(755, 462 , (159, 146, 105), tolerance=5):
                print("dar clicl en buho")
                time.sleep(1)
                heart.click(941,284)
                time.sleep(.5)
                heart.click(973,297)
               
            if heart.pixelMatchesColor(376,250,(255, 208, 102), tolerance=15):
                print("detectar ventana del buho ") 
                time.sleep(.5)
                heart.click(421,458,clicks=2,interval=.2)
                cont = 0
                while True:
                    if heart.pixelMatchesColor(376,250,(255, 208, 102), tolerance=15) :
                        print("cierra bien")
                        time.sleep(1)
                        break
                    if cont == 50:
                        print("cierra con contador")
                        break
                    cont = cont + 1
                    time.sleep(.1)    
            print("ventana de banco--> dar cliclc pestaña recurso")  
            time.sleep(.5)  
            if heart.pixelMatchesColor(1227,249 , (255, 255, 255), tolerance=15) :
                print("ventana de banco--> dar cliclc pestaña recurso")
                while True:
                    "recurso bancoi"
                    time.sleep(2)
                    heart.click(426,299)
                    time.sleep(.5)

                    print("pestaña recurso inventario")
                    heart.click(1098, 300)
                    time.sleep(.5)
                    if not heart.pixelMatchesColor(1051,368,(190, 185, 152), tolerance=15) :
                        print("sale por que detecta")
                        break



                while True:
                    time.sleep(.5)
                    print("intentando pasar el recurso")
                    "recurso detectado"
                    
                    
                    recnec()
                    
                    " ver que esta en pestaña recurso y pasar el recurso"
                    if heart.pixelMatchesColor(424,291,( 81,  74,  60), tolerance=15) :
                        time.sleep(1)
                        print("buscar el recurso y pasarlo al inventario")
                        time.sleep(.5)
                        heart.moveTo(1049,364)                       
                        heart.keyDown("ctrl")
                        time.sleep(.3)
                        heart.click(clicks=2,interval=.2)
                        heart.mouseUp()
                        time.sleep(.3)
                        heart.keyUp("ctrl")
                        time.sleep(.3)
                        heart.click(1249,267)
                        
                        break
                if heart.pixelMatchesColor(1053,369 ,(190, 185, 152), tolerance=5):
                    heart.click(1250,263)
                    time.sleep(.5)
                    print("hay un recurso en inventario")
                    time.sleep(.5)
                    break
            break
               
def aceptar_intercambio():
    while True:
        print("esperando el inercambio")
        #ventana aceptar inter
        if heart.pixelMatchesColor(1024,404,(255, 255, 255), tolerance=5):
            time.sleep(.5)
            heart.click(771,444)
        #ventana del intercambio
        if heart.pixelMatchesColor(1259,274,(255, 255, 255), tolerance=5):

            while True:
                if not heart.pixelMatchesColor(405,553 ,(190, 185, 152), tolerance=5):
                    print("detecta el recurso")
                    time.sleep(2)
                    break 
            while True:
                if heart.pixelMatchesColor(1238,648,(255,  97,   0), tolerance=5):
                    print("listo para dar intercambio")  
                    time.sleep(.5)
                    heart.click(1245,651,clicks=2,interval=.2)     
                    break 
            while True:
                if not heart.pixelMatchesColor(853, 306 ,(255, 255, 255), tolerance=5):      
                    break  
            time.sleep(.5)
            meter_recurso()


        





        

#ir_banco()
#hacer_anillos()
#vender()
ciclos = 0
while True:
    time.sleep(2)
    print("inicia")
    aceptar_intercambio()
    print("termina")
             






         
         
              
    
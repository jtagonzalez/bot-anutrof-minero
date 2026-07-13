import cv2 
import time
import numpy as np
import pyautogui
import pyautogui as heart
import os


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
            
            if not heart.pixelMatchesColor( 441,334 ,(129, 128,  33), tolerance=15) and heart.pixelMatchesColor(755, 462 , (159, 146, 105), tolerance=5):
                print("dar clicl en buho")
                time.sleep(1)
                heart.click(941,284)
                time.sleep(.3)
                heart.click(973,297)
               
            if heart.pixelMatchesColor(376,250,(255, 208, 102), tolerance=15):
                print("detectar ventana del buho ") 
                time.sleep(.5)
                heart.click(421,458)
                time.sleep(.5)
            print("ventana de banco--> dar cliclc pestaña recurso")    
            if heart.pixelMatchesColor(376,250,(255, 208, 102), tolerance=15) :
                "pestaña recurso inventario"
                heart.click(1098, 300)
                time.sleep(.5)
                
                "recurso bancoi"
                time.sleep(1)
                heart.click(426,299)
                time.sleep(1)

                



                while True:
                    time.sleep(.5)
                    print("intentando pasar el recurso")
                    "recurso detectado"
                    
                    
                    
                    if not heart.pixelMatchesColor(1226,249 , (255, 255, 255), tolerance=5) :
                        print("entra al wile a pasar las cosas")
                        time.sleep(10)
                        
                        print("entra a cerrar si no detecta la ventana se recurso")
                        break
                    " ver que esta en pestaña recurso y pasar el recurso"
                    if heart.pixelMatchesColor(424,291,( 81,  74,  60), tolerance=15) :
                        """mover el recurso mio acaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"""
                        time.sleep(1)
                        print("buscar el recurso y pasarlo al inventario")
                        time.sleep(.5)
                        heart.moveTo(534,409)                       
                        heart.mouseDown()
                        time.sleep(.3)
                        heart.moveTo(1228,416)
                        heart.mouseUp()
                        time.sleep(.3)
                        heart.write("1000", interval=0.4)
                        time.sleep(.3)
                        heart.press("enter")
                        time.sleep(.3)
                        break
            if not heart.pixelMatchesColor(1053,369 ,(190, 185, 152), tolerance=5) or not  heart.pixelMatchesColor(1044,367 ,(190, 185, 152), tolerance=5) or not heart.pixelMatchesColor(1054,357 ,(190, 185, 152), tolerance=5) or not heart.pixelMatchesColor(1066,368 ,(190, 185, 152), tolerance=5) or not heart.pixelMatchesColor(1053,377 ,(190, 185, 152), tolerance=5) and heart.pixelMatchesColor(1264,389 , (255, 255, 255), tolerance=5):
                heart.click(1250,263)
                time.sleep(.5)
                print("hay un recurso en inventario")
                time.sleep(1)
                break    
                    
        intercambio()                
def intercambio():

    while True:
        #arriba
        """heart.click(1261,264)
        time.sleep(1)
        heart.click(1178,470)
        time.sleep(.5)"""
        #abajo
        heart.click(1257,296)
        time.sleep(1)
        heart.click(1210, 534)
        time.sleep(.5)
        
        if   heart.pixelMatchesColor(1017, 414,(255, 255, 255), tolerance=15):
            break
        if heart.pixelMatchesColor(1209,225, (255, 255, 255), tolerance=15):
            break

      

    while True:
        if heart.pixelMatchesColor(1209,225, (255, 255, 255), tolerance=15):
            
            while True:
                time.sleep(1)
                heart.click(930,271)
                time.sleep(1)

                #pasar el recurso
                heart.moveTo(885,346)
                time.sleep(.5)
                heart.keyDown("ctrl")
                heart.click(clicks=2,interval=.2)
                heart.keyUp("ctrl")
                time.sleep(.3)
                if not heart.pixelMatchesColor(901,556,(190, 185, 152), tolerance=15):
                    time.sleep(.3)
                    break
            while True:
                print("esperando para aceptar")
                if   heart.pixelMatchesColor(1233, 654 ,(255,  97,   0), tolerance=15):
                    heart.click(1138,654)
                #time.sleep(.5)
                if not heart.pixelMatchesColor(1200,223 , (255, 255, 255), tolerance=15):
                    break
            break
                    


        





        

#ir_banco()
#hacer_anillos()
#vender()
ciclos = 0
pasos = 0
while True:
    
    print("inicia")
    sacar_recurso()
    print("termina")
    pasos = pasos + 1
    if pasos == 50:
        print("termino")
        break             
    print(pasos)





         
         
              
    
import zmq
import json
import numpy as np
import cv2
import time
import math
import tensorflow as tf

from tensorflow.lite.python.interpreter import Interpreter
with open("model/labels.txt", 'r') as f:
  labels = [line.strip() for line in f.readlines()]
interpreter = Interpreter(model_path="model/detect.tflite")
interpreter.allocate_tensors() 


cap = cv2.VideoCapture("320x320_with_lines.avi") #il file palla_with_lines è stato creato solo a scopo di test per visualizzare i vari settori; le linee disegnate possono interferire con il riconoscimento della palla quando questa è in movimento
#cap = cv2.VideoCapture("lines.avi") #il file palla_with_lines è stato creato solo a scopo di test per visualizzare i vari settori; le linee disegnate possono interferire con il riconoscimento della palla quando questa è in movimento
ret,frame = cap.read()
frame = cv2.resize(frame,(320,320))
image_height, image_width, _ = frame.shape 

#angolo della testa iniziale
angolo_pitch_iniziale = math.radians(6.4)
#vettore calcolato a mano in base ai video di prova fatti con il robot;
#ogni valore in pixel corrisponde a una distanza di 10cm
vettore_distanze = [30,93,142,182,215,245,270,290,305]


while ret:
  
    im = frame

    #im = cv2.imdecode(np.frombuffer(im, np.uint8), cv2.IMREAD_COLOR)  
    im = cv2.resize(im,(320,320))
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = 160
    width = 160
    image_resized = cv2.resize(im, (width, height))
    input_data = np.expand_dims(image_resized, axis=0)
    mean = np.mean(input_data)
    std = np.std(input_data)
    input_data = (np.float32(input_data) - mean) / std
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[1]['index'])[0] 
    classes = interpreter.get_tensor(output_details[3]['index'])[0] 
    scores = interpreter.get_tensor(output_details[0]['index'])[0] 
    detections = []

    min_conf = 0.4
    if (scores[0] *100) > min_conf*100 :
        ymin = int(max(1,(boxes[0][0] * image_height)))
        xmin = int(max(1,(boxes[0][1] * image_width)))
        ymax = int(min(image_height,(boxes[0][2] * image_height)))
        xmax = int(min(image_width,(boxes[0][3] * image_width)))
    

        cv2.rectangle(im, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
        center_x = int(xmax - (xmax-xmin)/2)
        center_y = int(ymax - (ymax-ymin)/2)
        #print("center x, y: ", str(center_x), " ", str(center_y))
        center = (center_x,center_y)
        cv2.circle(im, center, 1, (255, 0, 255), 3)

        height = im.shape[0]
        width = im.shape[1]
        #print("w e h dell'immagine: ", str(width), " ",str(height))
        
        

        rotation = -45
        #poichè il conteggio dei pixel parte dall'alto, sono partito da 320 e ho sottratto il valore del centro per capire a che altezza si trovasse 
        distanza = 320 - (ymax - ((ymax-ymin)/2))

        distanza_minima = 305 #valore arbitrario
        for i in range(len(vettore_distanze)):
            if(abs((distanza - vettore_distanze[i])) < distanza_minima):
                #print("distanza: " + str(distanza) +"|" + "vettore distanze attuale: " + str(vettore_distanze[i]))
                #print(str(distanza - vettore_distanze[i]) +" < " + (str(distanza_minima)) )
                distanza_minima = distanza - vettore_distanze[i]
                posizione_vicina = i
                print()
        if(posizione_vicina > 3):
            print('posizione più vicina: ' + str(posizione_vicina+1))
        
        distanza_y = (10 * (posizione_vicina+1)) * math.cos(rotation)
        distanza_x = (10 * (posizione_vicina+1)) * math.sin(rotation)
        if(posizione_vicina > 3):
            print('distanza x ' + str(distanza_x) + "|" + 'distanza y ' + str(distanza_y))

    cv2.imshow("test",im)
    cv2.waitKey(500)
    ret,frame = cap.read()


import zmq
import json
import numpy as np
import cv2
import time
import math
import tensorflow as tf


def scambia_righe(matrice):
    n_righe = len(matrice)
    n_colonne = len(matrice[0])
    matriceNuova = np.zeros((n_righe, n_colonne))
    #creaiamo una nuova matrice a partire da quella passata in input che inverte la riga 1 con la riga "n_righe, la riga due scambiata con la riga n_righe-1 e così via"
    for i in range(n_righe):
        matriceNuova[i] = matrice[n_righe - 1 - i]
    return matriceNuova

def creaMatriceNegativaRibaltata(matrice):
    matriceNuova = -matrice
    matriceFinale=np.zeros((righe, colonne))
    #creiamo una nuova matrice che ha i coefficienti tutti negativi e la colonna 1 al posto della  colonna "colonne"
    for j in range(colonne):
        matriceFinale[:,j] = matriceNuova[:,colonne - 1 - j]
    return matriceFinale

from tensorflow.lite.python.interpreter import Interpreter
with open("model/labels.txt", 'r') as f:
  labels = [line.strip() for line in f.readlines()]
interpreter = Interpreter(model_path="model/detect.tflite")
interpreter.allocate_tensors() 
'''
context = zmq.Context()
socket = context.socket(zmq.REQ)
print(socket)

socket.connect("tcp://localhost:5555")
acquire = True

#focal = 450 #larghezza focale misurata della camera inferiore del robot
socket.send_string("alzaTesta")
r = socket.recv()
'''
cap = cv2.VideoCapture("palla_with_lines.avi") #il file palla_with_lines è stato creato solo a scopo di test per visualizzare i vari settori; le linee disegnate possono interferire con il riconoscimento della palla quando questa è in movimento
ret,frame = cap.read()
frame = cv2.resize(frame,(320,320))
image_height, image_width, _ = frame.shape 
distanza_verticale = 90 #cm, ossia il punto più lontano visto dal robot quando ha la testa ha un angolo di 8° rispetto al piano del pavimento
numero_elementi = 8 #ho deciso di dividere l'immagine in una matrice 8x8


#ho ristretto il problema al solo lato sinistro, poiché il destro può essere ricavato per simmetria in seguito
righe = 8
colonne = 4
lunghezza = []
larghezza = []
lunghezza_quadrato = distanza_verticale / numero_elementi  
for i in range(numero_elementi):
    lunghezza.append(i*lunghezza_quadrato)
    larghezza.append((i*lunghezza_quadrato+72)/3.6)

#print(lunghezza)
#print(larghezza)

larghezza_quadrato = np.zeros((righe, colonne))
for i in range (0,righe):
    for j in range(0,colonne):
        larghezza_quadrato[i][j] = (larghezza[i]*(j+1))/colonne
print()
#print(larghezza_quadrato)
matriceLarghezze = scambia_righe(larghezza_quadrato)
#print(matriceLarghezze)
matriceNegativa = creaMatriceNegativaRibaltata(matriceLarghezze)
#print(matriceNegativa)
matriceConcatenata = np.concatenate((matriceNegativa,matriceLarghezze), axis=1)
print("visualizzazione matrice comoda per noi")
print(matriceConcatenata)
print()
#print("visualizzazione matrice realmente utilizzata")
#matriceRobot = scambia_righe(matriceConcatenata)
#print(matriceRobot)
#print(matriceRobot[0][0])
#print(matriceRobot[7][7])


#divido l'immagine di 320px x 320px in 64 quadrati di 40px x 40px
quadrant_size = 40
num_quadrants_x = image_width // quadrant_size
num_quadrants_y = image_height // quadrant_size

dict={}

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
  min_conf = 0.2
  if (scores[0] *100) > min_conf*100 :
    ymin = int(max(1,(boxes[0][0] * image_height)))
    xmin = int(max(1,(boxes[0][1] * image_width)))
    ymax = int(min(image_height,(boxes[0][2] * image_height)))
    xmax = int(min(image_width,(boxes[0][3] * image_width)))
    
    
    cv2.rectangle(im, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

    height = im.shape[0]
    width = im.shape[1]
    print("w e h dell'immagine: ", str(width), " ",str(height))
    
    #individuo il quadrante in cui si trova la palla tra i 64 della griglia basandomi sul centro della palla
    center_x = int((xmax + xmin) // 2)
    center_y =int((ymax + ymin) // 2)
    print("center x, y: ", str(center_x), " ", str(center_y))



    quadrant_x = (center_x // quadrant_size)+1
    quadrant_y = (center_y // quadrant_size)+1
    print("quadrante x e y: ",str(quadrant_y) , " ",str(quadrant_x))

    



    print("")
    center = (center_x,center_y)
    cv2.circle(im, center, 1, (255, 0, 255), 3)

    cv2.imshow("test",im)
    cv2.waitKey(1000)


    y = (lunghezza_quadrato * (num_quadrants_y-quadrant_y)) + 30 #30 centimetri sono la distanza tra i piedi del robot e il primo punto osservato quando ha la testa dritta
    x = matriceConcatenata[quadrant_y-1][quadrant_x-1]
    #print(matriceRobot.shape)
    print("movimento lungo x e y:", str(x), " ",str(y))

    key = str(quadrant_y)+str(quadrant_x)
    print(key)
    if key not in dict:
        dict[key] = 1
    else:
        dict[key] += 1

    #cerchiamo il quadrante in cui la palla viene individuata più volte e poi ci muoviamo verso quello
    for key in dict:
        if dict[key] > 10:
            print("mi muovo verso il quadrante ", key)
    ''' scommentare per ottenere il movimento effettivo del robot
            Theta = math.pi/2.0 
            motionProxy.post.moveTo(x, y, Theta) 
            # wait is useful because with post moveTo is not blocking function 
            motionProxy.waitUntilMoveIsFinished()    
    '''
    
  ret,frame = cap.read()

    #else:
      #width = ymax -ymin

    #cv2.rectangle(im, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

    #dist = ((10*focal)/width) * math.atan(math.radians(47.64))
    #cv2.putText(im,str(int(dist)) , (xmin, ymin-7), cv2.FONT_HERSHEY_
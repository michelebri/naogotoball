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

context = zmq.Context()
socket = context.socket(zmq.REQ)
print(socket)

socket.connect("tcp://localhost:5555")
acquire = True

socket.send_string("alzaTesta")
r = socket.recv()

#angolo della testa iniziale
angolo_desiderato = math.radians(6.4)
motion.setAngles("HeadPitch",angolo_desiderato, 0.1)

while acquire:


	socket.send_string("acquisisci")

	im = socket.recv()

	im = cv2.imdecode(np.frombuffer(im, np.uint8), cv2.IMREAD_COLOR)  
	imH, imW, _ = im.shape 
	input_details = interpreter.get_input_details()
	output_details = interpreter.get_output_details()
	height = input_details[0]['shape'][1]
	width = input_details[0]['shape'][2]
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

	min_conf = 0.6
	if (scores[0] *100) > min_conf*100 :
		ymin = int(max(1,(boxes[0][0] * imH)))
		xmin = int(max(1,(boxes[0][1] * imW)))
		ymax = int(min(imH,(boxes[0][2] * imH)))
		xmax = int(min(imW,(boxes[0][3] * imW)))
		gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
		rows = gray.shape[0]
		cv2.rectangle(im, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
		ball_center = xmax - (xmax-xmin)/2
		if (ball_center >= width/2):
			int i = 0;
			while(!(ball_center >= (width/2)-5) and (ball_center <= (width/2)+5)):
				motion.setAngles(nomi_motori, 1, 0.5)
				i=i+1
			rotation = i
			distanza =ymax - (ymax-xmin)/2
		else:
			int i = 0;
			while(!(ball_center >= (width/2)-5) and (ball_center <= (width/2)+5)):
				motion.setAngles(nomi_motori, -1, 0.5)
				i=i+1
			rotation = -i
			distanza =ymax - (ymax-xmin)/2
	else:
		motion.setStiffnesses("Head", 1.0)
		# Definisci l'angolo di rotazione in radianti
		angolo_destra = 50  # 50 gradi a destra
		angolo_sinistra = -50  # 50 gradi a sinistra (negativo)

		# Imposta i nomi dei motori coinvolti
		nomi_motori = ["HeadYaw"]

		# Eseguo la rotazione a destra
		for i in range(0, angolo_destra)
			motion.setAngles(nomi_motori, 1, 0.5)
			if (scores[0] *100) > min_conf*100
				xmin = int(max(1,(boxes[0][1] * imW)))
				xmax = int(min(imW,(boxes[0][3] * imW)))
				ymin = int(max(1,(boxes[0][0] * imH)))
				ymax = int(min(imH,(boxes[0][2] * imH)))
				ball_center = xmax - (xmax-xmin)/2
				if ((ball_center >= (width/2)-5) and (ball_center <= (width/2)+5)):
					rotation = i
					distanza = ymax - (ymax-xmin)/2
					break
		if (rotation == None and distanza == None):

			#riporto la testa al centro

			motion.setAngles(nomi_motori, math.radians(0), 0.1)

			#e poi scansiono la parte a sinistra del robot

			for i in range(angolo_sinistra,0):
				motion.setAngles(nomi_motori, -1, 0.5)
				if (scores[0] *100) > min_conf*100:
					xmin = int(max(1,(boxes[0][1] * imW)))
					xmax = int(min(imW,(boxes[0][3] * imW)))
					ymin = int(max(1,(boxes[0][0] * imH)))
					ymax = int(min(imH,(boxes[0][2] * imH)))
					ball_center = xmax - (xmax-xmin)/2
					if ((ball_center >= (width/2)-5) and (ball_center <= (width/2)+5)):
						distanza = ymax - (ymax-xmin)/2
						rotation = -i
						break
		# Rilascia la rigidità dei motori
		motion.setStiffnesses("Head", 0.0)

		#vettore calcolato a mano in base ai video di prova fatti con il robot;
		#ogni valore in pixel corrisponde a una distanza di 10cm

		vettore_distanze = [30,93,142,182,215,245,270,290,305]
		
		distanza_minima = 305 #valore arbitrario
		for i in range(len(vettore_distanze)):
			if((distanza - vettore_distanze[i]) < distanza_minima):
				distanza_minima = vettore_distanze[i]
				posizione_vicina = i
		#la distanza lungo y viene ottenuta moltiplicando 10 cm * la posizione del vettore il cui numero di pixel si avvicina di più al centro della palla * coseno dell'angolo di rotazione
        #vengono aggiunti altri 10cm perché la prima linea che si vede in foto è a 20cm
		distanza_y =(15 + 10 * (posizione_vicina+1)) * math.cos(rotation)
		#la distanza lungo x sarà l'ipotenusa del rettangolo che si crea per il seno di rotation
		#vengono aggiunti altri 10cm perché il robot con quest'angolo inizia a vedere a 15cm dai suoi piedi
        distanza_x =(15 + 10 * (posizione_vicina+1)) * math.sin(rotation)

	cv2.imshow("frame",im)# Wait for a key event
	key = cv2.waitKey(1)

	# Check if the 'Esc' key was pressed
	if key == 27:
		cv2.destroyAllWindows()
		acquire = False
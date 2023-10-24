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
angolo_pitch_iniziale = math.radians(6.4)
motion.setAngles("HeadPitch",angolo_desiderato, 0.1)
#vettore calcolato a mano in base ai video di prova fatti con il robot;
#ogni valore in pixel corrisponde a una distanza di 10cm
vettore_distanze = [30,93,142,182,215,245,270,290,305]


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

	min_conf = 0.4
	if (scores[0] *100) > min_conf*100 :
		xmin = int(max(1,(boxes[0][1] * image_width)))
		xmax = int(min(image_width,(boxes[0][3] * image_width)))
		ymin = int(max(1,(boxes[0][0] * image_height)))
		ymax = int(min(image_height,(boxes[0][2] * image_height)))
		cv2.rectangle(im, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
		x_center = xmax - (xmax-xmin)/2
		int i = 0;
		if (x_center >= width/2):
			while((x_center <= (width/2)-5) or (x_center >= (width/2)+5)):
				motion.setAngles(nomi_motori, 1, 0.5)
				i=i+1
			rotation = i
			distanza = ymax - (ymax-xmin)/2
		else:
			while((x_center <= (width/2)-5) or (x_center >= (width/2)+5)):
				motion.setAngles(nomi_motori, -1, 0.5)
				i=i+1
			rotation = -i
			distanza = ymax - (ymax-xmin)/2
	else:
		motion.setAngles(nomi_motori, math.radians(0), 0.1)
		angolo_destra = 50  # 50 gradi a destra
		angolo_sinistra = 50  # 50 gradi a sinistra

		# Imposto il nome del motore coinvolto
		nomi_motori = ["HeadYaw"]

		# Eseguo la rotazione a destra
		for i in range(0, angolo_destra)
			motion.setAngles(nomi_motori, 1, 0.5)
			if (scores[0] *100) > min_conf*100
				xmin = int(max(1,(boxes[0][1] * image_width)))
				xmax = int(min(image_width,(boxes[0][3] * image_width)))
				ymin = int(max(1,(boxes[0][0] * image_height)))
				ymax = int(min(image_height,(boxes[0][2] * image_height)))
				cv2.rectangle(im, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
				x_center = xmax - (xmax-xmin)/2
				if ((x_center >= (width/2)-5) and (x_center <= (width/2)+5)):
					rotation = i
					distanza = ymax - (ymax-xmin)/2
					break
		if (rotation == None and distanza == None):

			#riporto la testa al centro

			motion.setAngles(nomi_motori, math.radians(0), 0.1)

			#e poi scansiono la parte a sinistra del robot

			for i in range(0, angolo_sinistra):
				motion.setAngles(nomi_motori, -1, 0.5)
				if (scores[0] *100) > min_conf*100:
					xmin = int(max(1,(boxes[0][1] * image_width)))
					xmax = int(min(image_width,(boxes[0][3] * image_width)))
					ymin = int(max(1,(boxes[0][0] * image_height)))
					ymax = int(min(image_height,(boxes[0][2] * image_height)))
					cv2.rectangle(im, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
					x_center = xmax - (xmax-xmin)/2
					if ((x_center >= (width/2)-5) and (x_center <= (width/2)+5)):
						distanza = ymax - (ymax-xmin)/2
						rotation = -i
						break		
		distanza_minima = 305 #valore arbitrario
		for i in range(len(vettore_distanze)):
			if((distanza - vettore_distanze[i]) < distanza_minima):
				distanza_minima = vettore_distanze[i]
				posizione_vicina = i
		#la distanza lungo y viene ottenuta moltiplicando 10 cm * la posizione del vettore il cui numero di pixel si avvicina di più al centro della palla * coseno dell'angolo di rotazione
		distanza_y =(10 * (posizione_vicina+1)) * math.cos(rotation)
		#la distanza lungo x sarà l'ipotenusa del rettangolo che si crea per il seno di rotation
        distanza_x =(10 * (posizione_vicina+1)) * math.sin(rotation)

	cv2.imshow("frame",im)# Wait for a key event
	key = cv2.waitKey(1)

	# Check if the 'Esc' key was pressed
	if key == 27:
		cv2.destroyAllWindows()
		acquire = False
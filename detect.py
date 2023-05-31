import zmq
import json
import numpy as np
import cv2

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

while acquire:


	socket.send_string("acquisisci")

	im = socket.recv()

	posizione = 0.99

	im = cv2.imdecode(np.frombuffer(im, np.uint8), cv2.IMREAD_COLOR)  
	im = cv2.resize(im,(640,480)) 
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

	min_conf = 0.1
	for i in range(len(scores)):
		if ((scores[i].any() > min_conf) and (scores[i].any() <= 1.0)):
		  
			object_name = labels[int(classes[i])]
			if (scores[i] *100) > min_conf*100 :
				ymin = int(max(1,(boxes[i][0] * imH)))
				xmin = int(max(1,(boxes[i][1] * imW)))
				ymax = int(min(imH,(boxes[i][2] * imH)))
				xmax = int(min(imW,(boxes[i][3] * imW)))
				if  "ball" in object_name:
					cv2.rectangle(im, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

					label = '%s' % (object_name) 
					labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) 
					label_ymin = max(ymin, labelSize[1] + 10) 
					cv2.rectangle(im, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) 
					cv2.putText(im, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) 

	cv2.imshow("frame",im)# Wait for a key event
	key = cv2.waitKey(1)

	# Check if the 'Esc' key was pressed
	if key == 27:
		cv2.destroyAllWindows()
		acquire = False
import zmq
import cv2
from naoqi import ALProxy
import numpy as np 
from PIL import Image

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
videoDevice = ALProxy('ALVideoDevice', "nao.local.", 9559)

AL_kTopCamera = 1
AL_kQVGA = 2           
AL_kBGRColorSpace = 13
captureDevice = videoDevice.subscribeCamera("scatvcaataa", 1,1, 13, 30)

while True:
    message = socket.recv()


    if(message == "acquisisci"):
            result = videoDevice.getImageRemote(captureDevice)
            videoDevice.releaseImage(captureDevice)
            im = Image.frombytes("RGB", (result[0], result[1]), result[6])
            cvim = np.array(im)
            frame_enc = cv2.imencode(".jpg", cvim)[1].tobytes()
            socket.send(frame_enc)
    else:
        break
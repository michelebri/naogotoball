import cv2
import numpy as np

# Percorso del video da leggere e video risultante da scrivere
input_video_path = "320x320.avi"
output_video_path = "320x320_with_lines.avi"

# Leggi il video
#video_capture = cv2.VideoCapture(input_video_path)
video_capture = cv2.VideoCapture(input_video_path)

# Verifica che il video sia stato aperto correttamente
if not video_capture.isOpened():
    print("Errore nell'apertura del video.")
    exit()

frame_width = int(video_capture.get(3))
frame_height = int(video_capture.get(4))
print("frame w e h: " + str(frame_width) + " " + str(frame_height))

vettore = [30, 93, 142, 182, 215, 245, 270 ,290, 305]
#vettore = [290,270,245,215,182,142,93,30]
#print(str(step_x)," ", str(step_y))

# Definisci il codec e il video writer per scrivere il video risultante
codec = cv2.VideoWriter_fourcc(*'mp4v')
output_video = cv2.VideoWriter(output_video_path, codec, 30, (frame_width, frame_height))


while True:
    # Leggi un frame dal video
    ret, frame = video_capture.read()

    # Se non ci sono più frame da leggere, esci dal ciclo
    if not ret:
        break

    # Disegna le righe orizzontali
    for i in range(0,len(vettore)):
        y =  320 - vettore[i]
        cv2.line(frame, (0, y), (frame_width, y), (0, 0, 255), 1)  # Linea rossa

    # Mostra il frame con le righe e le colonne disegnate
    cv2.imshow("Video con righe e colonne", frame)

    # Scrivi il frame nel video risultante
    output_video.write(frame)

    # Se il tasto 'q' viene premuto, esci dal ciclo
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia le risorse
video_capture.release()
output_video.release()
cv2.destroyAllWindows()

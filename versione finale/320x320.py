import cv2

# Apre il video di input
video_input = cv2.VideoCapture('gianluca.mp4')

# Specifica le dimensioni del video di output (320x320)
width, height = 320, 320

# Definisce il codec e il video di output
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_output = cv2.VideoWriter('320x320.avi', fourcc, 30.0, (width, height))

while True:
    # Legge un frame dal video di input
    ret, frame = video_input.read()

    if not ret:
        break  # Esci se non ci sono più frame da leggere

    # Ridimensiona il frame al nuovo formato
    frame_resized = cv2.resize(frame, (width, height))

    # Scrive il frame ridimensionato nel video di output
    video_output.write(frame_resized)

# Chiude i video
video_input.release()
video_output.release()

# Chiude tutte le finestre
cv2.destroyAllWindows()
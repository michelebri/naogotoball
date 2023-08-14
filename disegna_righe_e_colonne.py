import cv2

# Percorso del video da leggere e video risultante da scrivere
input_video_path = "palla.avi"
output_video_path = "palla_with_lines.avi"

# Leggi il video
#video_capture = cv2.VideoCapture(input_video_path)
video_capture = cv2.VideoCapture("palla.avi")

# Verifica che il video sia stato aperto correttamente
if not video_capture.isOpened():
    print("Errore nell'apertura del video.")
    exit()

# Ottieni le dimensioni del video
frame_width = int(video_capture.get(3))
frame_height = int(video_capture.get(4))
print("frame w e h: " + str(frame_width) + " " + str(frame_height))

# Definisci le coordinate delle righe e delle colonne da disegnare
# Puoi regolare questi valori a seconda delle tue esigenze
# Ad esempio, disegnare una griglia 3x3 nel centro dell'immagine:
num_rows = 8
num_columns = 8
step_x = frame_width // (num_columns)
step_y = frame_height // (num_rows)
print(str(step_x)," ", str(step_y))

# Definisci il codec e il video writer per scrivere il video risultante
codec = cv2.VideoWriter_fourcc(*'mp4v')
output_video = cv2.VideoWriter(output_video_path, codec, 30, (frame_width, frame_height))

while True:
    # Leggi un frame dal video
    ret, frame = video_capture.read()

    # Se non ci sono più frame da leggere, esci dal ciclo
    if not ret:
        break

    # Disegna le righe verticali
    for i in range(1, num_columns + 1):
        x = i * step_x
        cv2.line(frame, (x, 0), (x, frame_height), (0, 0, 255), 1)  # Linea rossa

    # Disegna le righe orizzontali
    for i in range(1, num_rows + 1):
        y = i * step_y
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

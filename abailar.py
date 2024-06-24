import os

def install(libs):
    for lib in libs:
        os.system(f"pip install {lib} --upgrade ")

install(["urllib", "cv2", "mediapipe", "socket"])
import cv2
import mediapipe as mp
import requests
import socket
import urllib
import time

ascii = """ █████╗         ██████╗  █████╗ ██╗██╗      █████╗ ██████╗ ██╗
██╔══██╗        ██╔══██╗██╔══██╗██║██║     ██╔══██╗██╔══██╗██║
███████║        ██████╔╝███████║██║██║     ███████║██████╔╝██║
██╔══██║        ██╔══██╗██╔══██║██║██║     ██╔══██║██╔══██╗╚═╝
██║  ██║        ██████╔╝██║  ██║██║███████╗██║  ██║██║  ██║██╗
╚═╝  ╚═╝        ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝"""

hostname=socket.gethostname()

ip=requests.get('http://checkip.amazonaws.com').text.strip()

ipurl = urllib.parse.quote_plus(ip)

# URL del servidor donde enviar los datos
url = f"https://snapextensions.uni-goettingen.de/handleTextfile.php?type=write&filename=./textfiles/{ip}.poses"

os.system("cls")

print(ascii)

print(url)

time.sleep(2)

# Inicializar el objeto de mediapipe para reconocimiento de pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Inicializar la cámara frontal
cap = cv2.VideoCapture(0)

# Usar pose de cuerpo completo de Mediapipe
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        try:
            # Capturar frame de la cámara
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame.")
                break

            # Convertir la imagen de BGR a RGB
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detectar pose
            results = pose.process(image_rgb)

            # Obtener coordenadas x, y de la cara y las manos
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Coordenadas de la cara (nariz)
                face_x = landmarks[mp_pose.PoseLandmark.NOSE].x * frame.shape[1]
                face_y = landmarks[mp_pose.PoseLandmark.NOSE].y * frame.shape[0]

                # Coordenadas de la mano derecha (muñeca)
                right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
                if right_wrist.visibility > 0.5:
                    hand_x = right_wrist.x * frame.shape[1]
                    hand_y = right_wrist.y * frame.shape[0]
                else:
                    hand_x = None
                    hand_y = None

                # Mostrar las coordenadas en consola
                print(f"Cara - X: {face_x}, Y: {face_y}")
                print(f"Mano derecha - X: {hand_x}, Y: {hand_y}")

                # Enviar datos al servidor si las coordenadas de la mano son válidas
                if 1 == 1:
                    data = {"handx": hand_x, "handy": hand_y, "facex": face_x, "facey": face_y}
                    try:
                        response = requests.post(f"https://snapextensions.uni-goettingen.de/handleTextfile.php?type=write&content={data}&filename=./textfiles/{ip}.poses", data=data)
                        if response.status_code == 200:
                            print("Datos enviados correctamente.")
                        else:
                            print(f"Error al enviar datos. Código de estado: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error al enviar datos: {e}")
            else:
                print("No se detectaron landmarks.")
                requests.post(f"https://snapextensions.uni-goettingen.de/handleTextfile.php?type=write&content=no%20person%20located&filename=./textfiles/{ip}.poses", data=data)


            # Mostrar el frame con las anotaciones
            cv2.imshow('Pose Recognition', frame)

            # Salir del bucle si se presiona 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"Error inesperado: {e}")
            continue

# Liberar la cámara y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()

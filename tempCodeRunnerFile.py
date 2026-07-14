import cv2
import mediapipe as mp
import face_recognition
import numpy as np 

# --- Setup face recognition ---
known_image = face_recognition.load_image_file("me.jpg")  # a clear photo of your face
known_encoding = face_recognition.face_encodings(known_image)[0]

# --- Setup MediaPipe hands ---
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hand_detector = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=2)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # --- Face recognition ---
    face_locations = face_recognition.face_locations(rgb)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
        match = face_recognition.compare_faces([known_encoding], encoding, tolerance=0.5)
        label = "You" if match[0] else "Unknown"
        color = (0, 255, 0) if match[0] else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # --- Hand tracking ---
    hand_results = hand_detector.process(rgb)
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Face + Hand Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

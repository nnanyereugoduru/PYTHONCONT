import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import time
from PIL import Image, ImageOps

reference_path = r"C:\Projects\FOLDER1\PY1\me2.jpg"

# --- Load reference image with EXIF orientation fix ---
pil_img = Image.open(reference_path)
pil_img = ImageOps.exif_transpose(pil_img)
pil_img = pil_img.convert("RGB")

img = np.array(pil_img)
img = np.ascontiguousarray(img, dtype=np.uint8)

# Detect face in reference image
locs = face_recognition.face_locations(img, model="hog")

if len(locs) == 0:
    raise ValueError("No face detected in me2.jpg — use a clear, frontal photo.")

known_encoding = face_recognition.face_encodings(img, locs)[0]

# --- Setup MediaPipe Hands (single hand = faster) ---
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hand_detector = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=1)

# --- Setup webcam at a lower capture resolution ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

SCALE = 0.5          # downscale factor for face detection
DETECT_EVERY = 5     # only run face detection every N frames

frame_count = 0
face_locations = []
face_encodings = []
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)

    # --- Face recognition: only every few frames, on a downscaled image ---
    if frame_count % DETECT_EVERY == 0:
        small = cv2.resize(rgb, (0, 0), fx=SCALE, fy=SCALE)
        small = np.ascontiguousarray(small, dtype=np.uint8)

        raw_locations = face_recognition.face_locations(small, model="hog")
        face_encodings = face_recognition.face_encodings(small, raw_locations)

        # scale coordinates back up to full frame size
        inv = 1 / SCALE
        face_locations = [
            (int(top * inv), int(right * inv), int(bottom * inv), int(left * inv))
            for (top, right, bottom, left) in raw_locations
        ]

    frame_count += 1

    for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
        match = face_recognition.compare_faces([known_encoding], encoding, tolerance=0.5)
        label = "You" if match[0] else "Unknown"
        color = (0, 255, 0) if match[0] else (0, 0, 255)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # --- Hand tracking (runs every frame, it's already fast) ---
    hand_results = hand_detector.process(rgb)
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # --- FPS counter ---
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
    prev_time = curr_time
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Face + Hand Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hand_detector = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=2)

# Landmark indices
TIP_IDS = [4, 8, 12, 16, 20]        # thumb, index, middle, ring, pinky tips
PIP_IDS = [3, 6, 10, 14, 18]        # joint just below each tip

def get_finger_states(hand_landmarks, handedness_label):
    """Returns a list of 5 booleans: [thumb, index, middle, ring, pinky] — True = extended."""
    lm = hand_landmarks.landmark
    fingers = []

    # Thumb: compare x-position (sideways movement), flips depending on left/right hand
    if handedness_label == "Right":
        fingers.append(lm[TIP_IDS[0]].x < lm[PIP_IDS[0]].x)
    else:
        fingers.append(lm[TIP_IDS[0]].x > lm[PIP_IDS[0]].x)

    # Other 4 fingers: tip above its PIP joint (smaller y = higher on screen) = extended
    for tip_id, pip_id in zip(TIP_IDS[1:], PIP_IDS[1:]):
        fingers.append(lm[tip_id].y < lm[pip_id].y)

    return fingers  # e.g. [False, True, True, False, False]

def classify_gesture(fingers):
    thumb, index, middle, ring, pinky = fingers

    if fingers == [False, False, False, False, False]:
        return "Fist"
    if fingers == [True, True, True, True, True]:
        return "Open palm"
    if fingers == [False, True, False, False, False]:
        return "Pointing"
    if fingers == [False, True, True, False, False]:
        return "Peace sign"
    if fingers == [True, False, False, False, False]:
        return "Thumbs up"
    if fingers == [True, True, False, False, True]:
        return "Rock on"
    if fingers == [False, True, False, False, True]:
        return "Call me?"  # ambiguous pattern, just an example
    return "Unknown gesture"

cap = cv2.VideoCapture(0)
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hand_results = hand_detector.process(rgb)

    if hand_results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(
            hand_results.multi_hand_landmarks, hand_results.multi_handedness
        ):
            label = handedness.classification[0].label  # "Left" or "Right"
            fingers = get_finger_states(hand_landmarks, label)
            gesture = classify_gesture(fingers)

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Draw the gesture label near the wrist point
            wrist = hand_landmarks.landmark[0]
            h, w, _ = frame.shape
            x, y = int(wrist.x * w), int(wrist.y * h)
            cv2.putText(frame, gesture, (x - 20, y + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
    prev_time = curr_time
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Hand Gesture Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
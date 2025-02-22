import cv2
import mediapipe as mp
import serial
import time
import math

# Set up serial communication (update the COM port as per your system)
arduino = serial.Serial('COM9', 9600)  # Replace 'COM4' with your Arduino's COM port
time.sleep(2)  # Wait for Arduino to initialize

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Function to map distance to servo angle
def map_distance_to_angle(distance, min_dist, max_dist, min_angle, max_angle):
    return int((distance - min_dist) * (max_angle - min_angle) / (max_dist - min_dist) + min_angle)

# OpenCV video capture
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    # Convert to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get thumb tip and index finger tip coordinates
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            h, w, _ = img.shape
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)

            # Draw a line between the thumb and index finger
            cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 3)
            cv2.circle(img, (thumb_x, thumb_y), 5, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (index_x, index_y), 5, (0, 255, 0), cv2.FILLED)

            # Calculate distance
            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)

            # Map the distance to servo angle (0-90 degrees)
            angle = map_distance_to_angle(distance, min_dist=50, max_dist=200, min_angle=0, max_angle=180)
            angle = max(0, min(180, angle))  # Ensure angle is within bounds

            # Send angle to Arduino
            arduino.write(f"{angle}\n".encode())

            # Display distance and angle
            cv2.putText(img, f"Angle: {angle} deg", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Draw landmarks
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the image
    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
arduino.close()

import cv2
import mediapipe as mp
import time
import math
import csv

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Function to map distance to angle (0-180 degrees)
def map_distance_to_angle(distance, min_dist, max_dist, min_angle, max_angle):
    return int((distance - min_dist) * (max_angle - min_angle) / (max_dist - min_dist) + min_angle)

# Open a CSV file for daily logging
csv_filename = "daily_log.csv"
with open(csv_filename, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Angle"])  # CSV Header

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

            # Map the distance to servo angle (0-180 degrees)
            angle = map_distance_to_angle(distance, min_dist=50, max_dist=200, min_angle=0, max_angle=180)
            angle = max(0, min(180, angle))  # Ensure angle is within bounds

            # Display angle
            cv2.putText(img, f"Angle: {angle} deg", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Log the angle data into CSV
            with open(csv_filename, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), angle])

            # Draw landmarks
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the image
    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

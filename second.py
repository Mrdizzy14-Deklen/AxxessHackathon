import cv2
import mediapipe as mp
import serial
import time
import math
import csv

# Set up serial communication (update the COM port as per your system)
arduino = serial.Serial('COM5', 9600)  # Replace 'COM9' with your Arduino's COM port
time.sleep(2)  # Wait for Arduino to initialize

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# CSV File Setup
daily_log_file = "daily_joint_angles.csv"
with open(daily_log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Angle (degrees)"])

# Function to map distance to servo angle
def map_distance_to_angle(distance, min_dist, max_dist, min_angle, max_angle):
    return int((distance - min_dist) * (max_angle - min_angle) / (max_dist - min_dist) + min_angle)

# OpenCV video capture
cap = cv2.VideoCapture(0)


num_iterations = 7  # Set how many times you want to record data

for _ in range(num_iterations):
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

            # Calculate distance & angle
            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
            angle = map_distance_to_angle(distance, min_dist=50, max_dist=200, min_angle=0, max_angle=180)
            angle = max(0, min(180, angle))  

            # Save to CSV
            with open("daily_log.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([angle])

            print(f"Logged angle: {angle} degrees")

    # Display the image
    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

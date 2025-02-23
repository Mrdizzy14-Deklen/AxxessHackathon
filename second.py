import cv2
import mediapipe as mp
import time
import math
import csv
import os

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Function to map distance to angle (0-180 degrees)
def map_distance_to_angle(distance, min_dist, max_dist, min_angle, max_angle):
    return int((distance - min_dist) * (max_angle - min_angle) / (max_dist - min_dist) + min_angle)

# CSV filenames
csv_filename = "daily_log.csv"
weekly_log_filename = "weekly_log.csv"
monthly_log_filename = "monthly_log.csv"

# Initialize log files if they don't exist
def initialize_log_file(filename, headers):
    if not os.path.exists(filename):
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

initialize_log_file(csv_filename, ["Timestamp", "Angle"])  # Daily log
initialize_log_file(weekly_log_filename, ["Week", "Average Angle"])  # Weekly log
initialize_log_file(monthly_log_filename, ["Month", "Average Angle"])  # Monthly log

# OpenCV video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

logging = False  # Control variable for logging state

print("Press 's' to start recording for 15 seconds...")

# Display an initial frame to ensure the window opens
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read from camera.")
        break

    cv2.putText(frame, "Press 's' to start, 'q' to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Hand Tracking", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):  # Start logging when 's' is pressed
        logging = True
        start_time = time.time()  # Get the start time
        print("Logging started for 15 seconds...")
        break
    elif key == ord('q'):  # Quit the program if 'q' is pressed
        cap.release()
        cv2.destroyAllWindows()
        print("Program terminated successfully.")
        exit()

# Run loop for 15 seconds
while logging:
    elapsed_time = time.time() - start_time  # Time passed since start

    if elapsed_time > 15:  # Stop after 15 seconds
        logging = False
        print("15 seconds completed. Logging stopped.")
        break

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

            # Save the angle and timestamp to the CSV
            with open(csv_filename, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), angle])

            # Draw landmarks
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the image
    cv2.imshow("Hand Tracking", img)

    # Press 'q' anytime to quit early
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        logging = False
        print("Logging stopped manually.")
        break

# Process daily average and update weekly/monthly logs
daily_angles = []
with open(csv_filename, "r") as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        daily_angles.append(int(row[1]))

# Compute and store the daily average
if daily_angles:
    average_angle = sum(daily_angles) / len(daily_angles)

    # Append to weekly_log (uses current week number)
    current_week = time.strftime("%U")  # Week number (0-51)
    with open(weekly_log_filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([current_week, average_angle])

    # Append to monthly_log (uses current month number)
    current_month = time.strftime("%m")  # Month number (01-12)
    with open(monthly_log_filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([current_month, average_angle])

    # Reset daily log for the next day
    with open(csv_filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Angle"])  # Reset the daily log header

    print(f"Daily average angle {average_angle} logged to weekly and monthly logs.")

# Cleanup: Close OpenCV window and release resources
cap.release()
cv2.destroyAllWindows()
print("Program terminated successfully.")

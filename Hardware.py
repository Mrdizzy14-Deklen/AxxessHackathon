import time
import serial
import math
import cv2
import mediapipe as mp
import sys



# Define the COM port
arduino_port_name = input('What is the COM port?')

# Try to open the serial connection
try:
    arduino_port = serial.Serial(arduino_port_name, 9600)
    print(f"Connected to Arduino on {arduino_port_name}!")
    time.sleep(2)
except serial.SerialException:
    print(f"Error: Could not find {arduino_port_name}. Terminating program.")
    sys.exit()

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hand_tracker = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw_utils = mp.solutions.drawing_utils

def map_range(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Start the webcam capture
camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hand_tracker.process(frame_rgb)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            frame_height, frame_width, _ = frame.shape
            thumb_x, thumb_y = int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height)
            index_x, index_y = int(index_tip.x * frame_width), int(index_tip.y * frame_height)

            cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 3)
            cv2.circle(frame, (thumb_x, thumb_y), 5, (0, 255, 0), cv2.FILLED)
            cv2.circle(frame, (index_x, index_y), 5, (0, 255, 0), cv2.FILLED)

            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)

            servo_angle = map_range(distance, in_min=50, in_max=200, out_min=0, out_max=180)
            servo_angle = max(0, min(180, servo_angle))  

            # Write the servo angle to Arduino
            arduino_port.write(f"{servo_angle}\n".encode())

            # Display the angle on the video feed
            cv2.putText(frame, f"Angle: {servo_angle} deg", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Draw the hand landmarks
            mp_draw_utils.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
camera.release()
cv2.destroyAllWindows()

# Close the Arduino connection
arduino_port.close()

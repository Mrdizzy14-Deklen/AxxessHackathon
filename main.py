import serial
import time

ser = serial.Serial('COM3', 115200)  # Change COM port

def get_motor_angle():
    line = ser.readline().decode().strip()
    angle_x, angle_y = map(float, line.split(","))
    return angle_x, angle_y

while True:
    angle_x, angle_y = get_motor_angle()
    print(f"Motor Angle X: {angle_x:.2f} | Motor Angle Y: {angle_y:.2f}")
    time.sleep(0.1)

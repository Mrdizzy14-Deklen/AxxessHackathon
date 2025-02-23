#include <Servo.h>

Servo myServo;
int angle;

void setup() {
  myServo.attach(9);  // Servo connected to pin 9
  Serial.begin(9600); // Start serial communication
}

void loop() {
  if (Serial.available() > 0) {
    angle = Serial.parseInt();  // Read the angle from Python

    if (angle >= 0 && angle <= 180) {
      if (angle > 90) {
        myServo.write(0);  // Rotate clockwise (full speed)
      } else if (angle < 90) {
        myServo.write(180);    // Rotate counterclockwise (full speed)
      } else {
        myServo.write(90);   // Stop the motor
      }
    }
  }
}

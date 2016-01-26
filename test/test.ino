#include <SDPArduino.h>
#include <Wire.h>

#define REAR_WHEEL_MOTOR 0
#define LEFT_WHEEL_MOTOR 1
#define RIGHT_WHEEL_MOTOR 2
#define KICKER_MOTOR 3

#define FORWARD 'W'
#define BACK 'S'
#define LEFT 'A'
#define RIGHT 'D'

void setup() {
  SDPsetup();
  motorAllStop();
}

void loop() {
  if (Serial.available() > 0) {
    byte command = Serial.read();
    if (command == '3') {
      Serial.println("KICKER");
      moveKicker();
    } else if (command == '0') {
      Serial.println("REAR");
      moveRearWheel();
    } else if (command == '1') {
      Serial.println("LEFT");
      moveLeftWheel();
    } else if (command == '2') {
      Serial.println("RIGHT");
      moveRightWheel();
    } else if (command == FORWARD) {
      Serial.println(FORWARD);
      moveForw();
    } else if (command == BACK) {
      Serial.println(BACK);
      moveBack();
    } else {
      Serial.println("Invalid command was entered,");
    }
    motorAllStop();
  }
}

//void moveForward() {
//  motorForward();
//}

void moveKicker() {
  motorForward(KICKER_MOTOR, 100);
  delay(500);
}

void moveRearWheel() {
  motorBackward(REAR_WHEEL_MOTOR, 100);
  delay(500);
}

void moveLeftWheel() {
  motorBackward(LEFT_WHEEL_MOTOR, 100);
  delay(500);
}

void moveBack() {
  motorBackward(LEFT_WHEEL_MOTOR, 100);
  motorForward(RIGHT_WHEEL_MOTOR, 100);
  delay(1000);
}

void moveForw() {
  motorForward(LEFT_WHEEL_MOTOR, 100);
  motorBackward(RIGHT_WHEEL_MOTOR, 100);
  delay(1000);
}

void moveRightWheel() {
  motorBackward(RIGHT_WHEEL_MOTOR, 100);
  delay(500);
}

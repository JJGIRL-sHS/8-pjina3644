#include "motor.h"
#include "config.h"
#include <Servo.h>

static Servo myServo;

void initMotor() {
  myServo.attach(PIN_SERVO);
  myServo.write(SERVO_OPEN);
}

void openValve() {
  myServo.write(SERVO_OPEN);
}

void lockValve() {
  myServo.write(SERVO_LOCK);
}
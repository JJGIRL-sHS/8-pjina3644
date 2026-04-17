#include "alert.h"
#include "config.h"
#include <Arduino.h>

void initAlert() {
  pinMode(PIN_LED_GREEN,  OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED,    OUTPUT);
  pinMode(PIN_BUZZER,     OUTPUT);
  // 버저 OFF 상태가 HIGH (능동부저는 LOW=ON)
  digitalWrite(PIN_BUZZER, HIGH);
}

void setLED(bool green, bool yellow, bool red) {
  digitalWrite(PIN_LED_GREEN,  green  ? HIGH : LOW);
  digitalWrite(PIN_LED_YELLOW, yellow ? HIGH : LOW);
  digitalWrite(PIN_LED_RED,    red    ? HIGH : LOW);
}

void buzzerWarning() {
  for (int i = 0; i < 2; i++) {
    digitalWrite(PIN_BUZZER, LOW);
    delay(200);
    digitalWrite(PIN_BUZZER, HIGH);
    delay(400);
  }
}

void buzzerLock() {
  digitalWrite(PIN_BUZZER, LOW);
  delay(800);
  digitalWrite(PIN_BUZZER, HIGH);
  delay(100);
}

void buzzerOff() {
  digitalWrite(PIN_BUZZER, HIGH);
}
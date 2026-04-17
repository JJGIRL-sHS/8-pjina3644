#include "sensor.h"
#include "config.h"
#include <Arduino.h>

void initSensors() {
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
}

float getDistanceCM() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 30000);
  if (duration == 0) return 999.0;
  return duration * 0.034 / 2.0;
}

// ── 사운드 센서 5회 평균 샘플링 ────────────────────────
// 단일 analogRead는 노이즈에 취약 → 평균값으로 안정화
bool isWaterFlowing() {
  long sum = 0;
  const int SAMPLES = 5;
  for (int i = 0; i < SAMPLES; i++) {
    sum += analogRead(PIN_SOUND);
    delay(10);
  }
  int avg = sum / SAMPLES;
  return (avg > SOUND_THRESHOLD);
}

// ── 초음파 센서 3회 중간값(median) ─────────────────────
// 이상치(튐 값) 한 번으로 오작동하는 것을 방지
bool isPersonNear() {
  float readings[3];
  for (int i = 0; i < 3; i++) {
    readings[i] = getDistanceCM();
    delay(20);
  }
  // 간단 정렬 (버블)
  for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 2 - i; j++) {
      if (readings[j] > readings[j + 1]) {
        float tmp = readings[j];
        readings[j] = readings[j + 1];
        readings[j + 1] = tmp;
      }
    }
  }
  float median = readings[1]; // 중간값
  return (median < PERSON_DIST_CM);
}
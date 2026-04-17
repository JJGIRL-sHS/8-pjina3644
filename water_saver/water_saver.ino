#include <ArduinoJson.h>

#include "config.h"
#include "sensor.h"
#include "alert.h"
#include "motor.h"

unsigned long flowStartTime = 0;
bool isWarned  = false;
bool isLocked  = false;

// ── 디바운스용 카운터 ──────────────────────────────
// 물 흐름 / 사람 감지가 연속 N번 같은 결과일 때만 상태 전환
// → 센서 노이즈로 인한 순간 튐 방지
static int  waterOnCount  = 0;   // 연속 감지 횟수
static int  waterOffCount = 0;   // 연속 미감지 횟수
static bool waterState    = false;

static const int DEBOUNCE_COUNT = 1; // 연속 3회 일치 시 상태 변경

unsigned long lastSentTime;
unsigned long interval = 500; 

void setup() {
  Serial.begin(9600);
  initSensors();
  initAlert();
  initMotor();
  setLED(true, false, false);
}


void loop() {
  
  // ── 1. 센서 원시값 읽기 ─────────────────────────
  bool rawWater  = isWaterFlowing(); // sensor.cpp 내부에서 5회 평균
  bool personOn  = isPersonNear();
  
  
  // ── 2. 물 흐름 디바운스 처리 ────────────────────
  if (rawWater) {
    waterOnCount++;
    waterOffCount = 0;
    if (waterOnCount >= DEBOUNCE_COUNT) waterState = true;
  } else {
    waterOffCount++;
    waterOnCount = 0;
    if (waterOffCount >= DEBOUNCE_COUNT) waterState = false;
  }

  // ── 3. 정상 상태 (물 없음 or 사람 있음) ──────────
  if (!waterState || personOn) {
    flowStartTime = 0;
    isWarned      = false;
    if (isLocked) {
      openValve();
      isLocked = false;
      Serial.println("수도 열림");
    }
    setLED(true, false, false);
    buzzerOff();
    delay(300);
  }

  // // ── 4. 물 흐름 시작 타이머 ──────────────────────
  // if (flowStartTime == 0) {
  //   flowStartTime = millis();
  //   Serial.println("물 흐름 감지 시작");
  // }

  unsigned long elapsed = (millis() - flowStartTime) / 1000;

  // // ── 5. 단계별 경보 처리 ─────────────────────────
  if (elapsed >= WARNING_SEC && !isWarned) {
    setLED(false, true, false);
    buzzerWarning();
    isWarned = true;
    Serial.print("{\"event\":\"warning\",\"elapsed\":");
    Serial.print(elapsed);
    Serial.println("}");
    Serial.println("경고: 수도 방치 중!");
  }
  // } else if (elapsed < WARNING_SEC) {
  //   setLED(true, false, false);
  //   // 1초마다 상태 JSON 전송
  //   static unsigned long lastReport = 0;
  //   if (millis() - lastReport >= 1000) {
  //     Serial.print("{\"event\":\"flowing\",\"elapsed\":");
  //     Serial.print(elapsed);
  //     Serial.println("}");
  //     lastReport = millis();
  //   }
  // }

  
  measure();
  unsigned long currentTime = millis();
  if (currentTime - lastSentTime >= interval) {
    
    // TODO: 센서에서 값을 읽어오는 기능을 추가해주세요.
    int distance = getDistance();
    int decibel = getDecibel();

    JsonDocument doc;

    JsonArray items = doc["items"].to<JsonArray>();

    JsonObject obj1 = items.add<JsonObject>();
    obj1["type"] = "sonar";
    obj1["distance"] = distance;
    
    JsonObject obj2 = items.add<JsonObject>();
    obj2["type"] = "sound";
    obj2["decibel"] = decibel;

    serializeJson(doc, Serial);
    Serial.println();

    lastSentTime = currentTime;
  }


}
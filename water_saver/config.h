#ifndef CONFIG_H
#define CONFIG_H

// ── 핀 설정 ────────────────────────────────────────
#define PIN_TRIG        9
#define PIN_ECHO        8
#define PIN_SOUND       A0

#define PIN_LED_GREEN   4
#define PIN_LED_YELLOW  5
#define PIN_LED_RED     6

#define PIN_BUZZER      7
#define PIN_SERVO       3

// ── 동작 임계값 ────────────────────────────────────
#define PERSON_DIST_CM   80    // 사람 감지 거리 (cm)
#define SOUND_THRESHOLD  400   // 물 흐름 감지 임계값 (0~1023)
#define WARNING_SEC      10    // 경고까지 허용 시간 (초)
#define LOCK_SEC         20    // 잠금까지 허용 시간 (초)

// ── 서보 각도 ──────────────────────────────────────
#define SERVO_OPEN       0
#define SERVO_LOCK       90

// ── 시리얼 통신 속도 ───────────────────────────────
// app.py 의 get_ser() 와 반드시 일치해야 합니다.
// app.py 기본값 115200 → 아두이노도 115200 으로 맞추거나
// 둘 다 9600 으로 통일하세요. (현재: 9600)
#define SERIAL_BAUD      9600

#endif
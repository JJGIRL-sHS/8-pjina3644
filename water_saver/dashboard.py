"""
dashboard.py  ─  물 절약 시스템 실시간 대시보드
app.py 에서 st.Page("dashboard.py") 로 호출됩니다.
"""

import streamlit as st
import serial
import json
import time
from datetime import datetime
import pandas as pd

# ── 상수 ───────────────────────────────────────────────────────────────
MAX_LOG = 200          # 보관할 최대 로그 수
REFRESH_MS = 800       # 자동 새로고침 간격 (ms)

WARNING_SEC = 10       # config.h 와 동일하게 맞추세요
LOCK_SEC    = 20

# ── 세션 상태 초기화 ────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "logs":        [],          # {"time", "event", "elapsed"} 리스트
        "last_event":  "idle",      # idle | flowing | warning | lock
        "elapsed":     0,
        "valve_open":  True,
        "total_events": {"warning": 0, "lock": 0},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── 시리얼 읽기 ─────────────────────────────────────────────────────────
def read_serial(ser: serial.Serial | None):
    """버퍼에 쌓인 줄을 모두 읽어 로그에 추가, 마지막 이벤트 반환"""
    if ser is None or not ser.is_open:
        return

    lines_read = 0
    while ser.in_waiting and lines_read < 20:
        try:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()
        except Exception:
            break
        lines_read += 1

        if not raw.startswith("{"):
            # 일반 텍스트 로그 (한국어 상태 메시지)
            st.session_state.logs.append({
                "time":    datetime.now().strftime("%H:%M:%S"),
                "event":   "text",
                "message": raw,
                "elapsed": st.session_state.elapsed,
            })
        else:
            try:
                data = json.loads(raw)
                event   = data.get("event", "unknown")
                elapsed = int(data.get("elapsed", 0))

                st.session_state.last_event = event
                st.session_state.elapsed    = elapsed

                if event == "lock":
                    st.session_state.valve_open = False
                    st.session_state.total_events["lock"] += 1
                elif event in ("flowing", "warning"):
                    st.session_state.valve_open = True
                    if event == "warning":
                        st.session_state.total_events["warning"] += 1
                elif event == "idle":
                    st.session_state.valve_open = True

                st.session_state.logs.append({
                    "time":    datetime.now().strftime("%H:%M:%S"),
                    "event":   event,
                    "message": raw,
                    "elapsed": elapsed,
                })
            except json.JSONDecodeError:
                pass

    # 로그 크기 제한
    if len(st.session_state.logs) > MAX_LOG:
        st.session_state.logs = st.session_state.logs[-MAX_LOG:]


# ── 상태 → 표시 매핑 ────────────────────────────────────────────────────
EVENT_META = {
    "idle":     {"label": "대기 중",       "color": "#2ecc71", "icon": "💧"},
    "flowing":  {"label": "물 흐름 감지", "color": "#3498db", "icon": "🚿"},
    "warning":  {"label": "경고!",         "color": "#f39c12", "icon": "⚠️"},
    "lock":     {"label": "수도 잠금",     "color": "#e74c3c", "icon": "🔒"},
    "text":     {"label": "메시지",        "color": "#95a5a6", "icon": "📋"},
    "unknown":  {"label": "알 수 없음",    "color": "#95a5a6", "icon": "❓"},
}

def meta(event: str) -> dict:
    return EVENT_META.get(event, EVENT_META["unknown"])


# ── UI 렌더링 ───────────────────────────────────────────────────────────
read_serial(st.session_state.get("ser"))

ev   = st.session_state.last_event
m    = meta(ev)
el   = st.session_state.elapsed

# 1. 상태 배너
banner_color = m["color"]
st.markdown(
    f"""
    <div style="
        background:{banner_color}22;
        border-left:6px solid {banner_color};
        border-radius:8px;
        padding:16px 24px;
        margin-bottom:8px;
        font-size:1.4rem;
        font-weight:700;
        color:{banner_color};
    ">
        {m['icon']} &nbsp; 현재 상태: {m['label']}
        &nbsp;&nbsp;
        <span style="font-size:1rem;font-weight:400;color:#555;">
            경과 {el}초
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. KPI 카드 행
c1, c2, c3, c4 = st.columns(4)

valve_label = "🟢 열림" if st.session_state.valve_open else "🔴 잠김"
valve_color = "#2ecc71" if st.session_state.valve_open else "#e74c3c"

with c1:
    st.markdown(f"""
    <div style="background:{valve_color}22;border-radius:10px;padding:16px;text-align:center;">
        <div style="font-size:2rem;">{valve_label.split()[0]}</div>
        <div style="font-weight:700;">밸브 상태</div>
        <div style="color:{valve_color};font-weight:600;">{valve_label.split()[1]}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    pct = min(el / LOCK_SEC * 100, 100) if ev in ("flowing","warning","lock") else 0
    bar_color = "#e74c3c" if pct > 80 else "#f39c12" if pct > 40 else "#3498db"
    st.markdown(f"""
    <div style="background:#f0f2f6;border-radius:10px;padding:16px;text-align:center;">
        <div style="font-weight:700;margin-bottom:8px;">⏱ 사용 경과</div>
        <div style="font-size:1.8rem;font-weight:700;color:{bar_color};">{el}초</div>
        <div style="background:#ddd;border-radius:4px;height:8px;margin-top:6px;">
            <div style="background:{bar_color};width:{pct:.0f}%;height:8px;border-radius:4px;"></div>
        </div>
        <div style="font-size:0.75rem;color:#888;">{pct:.0f}% / {LOCK_SEC}초</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div style="background:#f39c1222;border-radius:10px;padding:16px;text-align:center;">
        <div style="font-size:2rem;">⚠️</div>
        <div style="font-weight:700;">누적 경고</div>
        <div style="font-size:1.6rem;font-weight:700;color:#f39c12;">
            {st.session_state.total_events['warning']}회
        </div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div style="background:#e74c3c22;border-radius:10px;padding:16px;text-align:center;">
        <div style="font-size:2rem;">🔒</div>
        <div style="font-weight:700;">누적 잠금</div>
        <div style="font-size:1.6rem;font-weight:700;color:#e74c3c;">
            {st.session_state.total_events['lock']}회
        </div>
    </div>""", unsafe_allow_html=True)

st.divider()

# 3. 타임라인 차트 + 로그 테이블
col_chart, col_log = st.columns([3, 2])

with col_chart:
    st.subheader("📈 이벤트 타임라인")
    df_events = pd.DataFrame([
        l for l in st.session_state.logs if l["event"] in ("flowing","warning","lock")
    ])
    if not df_events.empty:
        event_order = ["flowing", "warning", "lock"]
        event_num   = {"flowing": 1, "warning": 2, "lock": 3}
        df_events["level"] = df_events["event"].map(event_num)
        st.line_chart(
            df_events.set_index("time")["level"],
            color="#3498db",
            height=200,
        )
        st.caption("1=흐름감지 / 2=경고 / 3=잠금")
    else:
        st.info("아직 이벤트 데이터가 없습니다.")

with col_log:
    st.subheader("📋 최근 로그")
    recent = list(reversed(st.session_state.logs[-30:]))
    rows = []
    for l in recent:
        m_ = meta(l["event"])
        rows.append({
            "시각":   l["time"],
            "상태":   f"{m_['icon']} {m_['label']}",
            "메시지": l.get("message", ""),
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=240)
    else:
        st.info("수신 대기 중...")

st.divider()

# 4. 수동 제어 버튼 (대시보드 내 빠른 접근)
st.subheader("🎛 빠른 제어")
bc1, bc2, bc3 = st.columns(3)

ser = st.session_state.get("ser")

with bc1:
    if st.button("🚿 물 흐름 시뮬레이션 리셋", use_container_width=True):
        st.session_state.last_event = "idle"
        st.session_state.elapsed    = 0
        st.session_state.valve_open = True
        st.toast("상태가 리셋되었습니다.")

with bc2:
    if st.button("🔓 밸브 열기 명령 전송", use_container_width=True):
        if ser and ser.is_open:
            ser.write(b'{"cmd":"open"}\n')
            st.toast("밸브 열기 명령 전송!")
        else:
            st.warning("시리얼 미연결 상태입니다.")

with bc3:
    if st.button("🔒 밸브 잠금 명령 전송", use_container_width=True):
        if ser and ser.is_open:
            ser.write(b'{"cmd":"lock"}\n')
            st.toast("밸브 잠금 명령 전송!")
        else:
            st.warning("시리얼 미연결 상태입니다.")

# --- [기존 코드를 아래 내용으로 대체하세요] ---

# 5. 자동 새로고침 설정 (무한 새로고침 방지를 위해 주석 처리하거나 제거)
# 아래의 meta tag가 웹 브라우저를 강제로 새로고침하게 만들어 무한 루프를 발생시킵니다.
# st.markdown(
#     f"""<meta http-equiv="refresh" content="{REFRESH_MS // 1000}">""",
#     unsafe_allow_html=True,
# )

st.caption(f"🔄 자동 갱신 중지됨 (수동 확인 필요) | 시리얼: {'✅ 연결됨' if ser else '❌ 미연결'}")
st.info("💡 데이터 확인이 필요할 때 'R' 키를 누르거나 브라우저 새로고침을 해주세요.")
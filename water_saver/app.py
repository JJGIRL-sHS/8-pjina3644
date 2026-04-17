import streamlit as st
import serial
from datetime import datetime
import json
import os

# ── [1] 환경 설정 ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="물 절약 시스템",
    page_icon="💧",
    layout="wide",
)

# ── [2] 리소스 초기화 ──────────────────────────────────────────────────

@st.cache_resource
def get_ser(port: str, baud: int):
    """시리얼 포트를 열어 반환합니다."""
    try:
        ser = serial.Serial(port, baud, timeout=1)
        return ser
    except serial.SerialException:
        return None


def fetch_data():
    ser = st.session_state.ser
    while ser and ser.is_open and ser.in_waiting > 0:
        try:
            message = ser.readline().decode("utf-8").strip() 
            payload = json.loads(message)

            current_time = datetime.now()
            for item in payload["items"]:

                sensor_type = item["type"]
                
                if sensor_type == "sonar":
                    distance = item["distance"]
                    st.session_state.sonar_data.append({
                            "time": current_time,
                            "distance": distance,
                    })

                    st.session_state.current_distance = distance

                # 센서 값이 아날로그값인지 데시벨인지 단순히 소리가 났는지만 감지하는지 확인해주세요.
                if sensor_type == "sound":
                    decibel = item["decibel"]
                    st.session_state.sound_data.append({
                            "time": current_time,
                            "decibel": decibel,
                    })

                    st.session_state.current_decibel = decibel

        except json.JSONDecodeError as e:
            print(e)
        except Exception as e:
            print(e)

# ── [3] 사이드바: 연결 설정 ────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 연결 설정")
    port = st.text_input("시리얼 포트", value="COM6",
                         help="Windows: COM3~COM9 / Mac·Linux: /dev/tty.usbserial-...")
    baud = st.selectbox("보드레이트", [9600, 115200], index=0)

    if st.button("🔌 재연결"):
        get_ser.clear()

    ser = get_ser(port, baud)
    st.session_state.ser = ser

    if ser is not None and ser.is_open:
        st.success(f"✅ {port} @ {baud} 연결 성공!")
    else:
        st.error(f"❌ {port} 를 열 수 없습니다.")

    st.divider()
    st.caption("💡 아두이노가 연결되지 않아도 대시보드는 동작합니다.")

# ── [4] 세션 상태 공통 초기화 ──────────────────────────────────────────
for key, default in [
    ("sonar_data",        []),
    ("sound_data",        []),
    ("current_distance", None),
    ("current_decibel", None),
    ("angle",           90),
    ("last_sent_angle", 90),
    ("current_light",   0),
    ("logs",            []),
    ("last_event",      "idle"),
    ("elapsed",         0),
    ("valve_open",      True),
    ("total_events",    {"warning": 0, "lock": 0}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

    @st.fragment(run_every="0.3s")
    def collect_data():
        fetch_data()

    collect_data()

# ── [5] 멀티페이지 네비게이션 (챗봇 제외) ──────────────────────────────────
pages = [
    st.Page("dashboard.py", title="대시보드",  icon=":material/dashboard:",  default=True),
    st.Page("control.py",   title="수동 제어",  icon=":material/adjust:"),
]

page = st.navigation(pages=pages)
st.title(f"{page.icon} {page.title}")
page.run()
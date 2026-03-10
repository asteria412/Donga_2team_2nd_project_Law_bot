"""
Streamlit 메인 앱 - 탭 전체 진입점
실행: streamlit run front-end/mainapp.py
"""
import importlib.util
import os
import streamlit as st

st.set_page_config(
    page_title="LAWBOT",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 스타일 ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Streamlit 자동 pages/ 네비게이션 숨김 */
[data-testid="stSidebarNav"] { display: none; }

/* 사이드바 배경 */
[data-testid="stSidebar"] > div:first-child {
    background: #ffffff;
}

/* 로고 박스 */
.logo-box {
    background: #f0f4ff;
    border: 1px solid #d0dff5;
    border-radius: 16px;
    padding: 22px 16px 16px;
    text-align: center;
    margin-bottom: 12px;
}
.logo-emoji {
    font-size: 58px;
    line-height: 1;
    display: block;
    filter: drop-shadow(0 2px 6px rgba(100, 150, 220, 0.4));
}
.logo-title {
    font-size: 16px;
    font-weight: 700;
    color: #1a2a4a !important;
    margin-top: 10px;
    letter-spacing: 0.4px;
}
.logo-sub {
    font-size: 11px;
    color: #5a7ab5 !important;
    margin-top: 4px;
}

/* 목차 레이블 */
.toc-header {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #2c4a8a !important;
    padding: 4px 2px 2px;
}

/* 사이드바 텍스트 전체 */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #1a2a4a !important;
}

/* 라디오 버튼 항목 */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 3px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: 10px;
    padding: 9px 14px !important;
    font-size: 14px !important;
    transition: background 0.2s;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(44, 74, 138, 0.08) !important;
}

/* 구분선 */
[data-testid="stSidebar"] hr {
    border-color: #d0dff5;
}

/* info 박스 */
[data-testid="stSidebar"] [data-testid="stAlertContainer"] {
    background: #f0f4ff !important;
    border: 1px solid #d0dff5 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── 사이드바 로고 영역 ───────────────────────────────────────────────
st.sidebar.markdown("""
<div class="logo-box">
  <span class="logo-emoji">⚖️</span>
  <div class="logo-title">법령 요약 시스템</div>
  <div class="logo-sub">2조 법령 요약 에이전트 v1.0</div>
</div>
""", unsafe_allow_html=True)

# ── 세션 상태 초기화 ─────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api"
if "api_base" not in st.session_state:
    st.session_state.api_base = API_BASE

# ── 목차 네비게이션 ──────────────────────────────────────────────────
st.sidebar.markdown('<div class="toc-header">📋 목차</div>', unsafe_allow_html=True)

pages = {
    "📊 리스크 현황":   "pages/1리스크현황.py",
    "🗂️ 부서별 보관함": "pages/2부서별보관함.py",
    "📋 리포트 센터":   "pages/3리포트센터.py",
    "💬 판례 챗봇":     "pages/4판례챗봇.py",
    "📝 숙지 퀴즈":     "pages/5숙지_퀴즈.py",
}

selected = st.sidebar.radio("목차", list(pages.keys()), label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.info(f"🔌 API: {API_BASE}")

# ── 선택된 페이지 콘텐츠 인라인 로드 ─────────────────────────────────
page_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pages[selected])

try:
    spec = importlib.util.spec_from_file_location("current_page", page_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
except Exception as e:
    if "StopException" not in type(e).__name__:
        st.error(f"페이지 로드 오류: {e}")

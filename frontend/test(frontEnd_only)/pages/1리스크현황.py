"""
탭 1: 리스크 현황 대시보드
- 최근 수집 법령 목록
- 부서별 법령 현황 차트
- LangSmith 토큰 모니터링 링크
"""
import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000/api"

st.title("📊 리스크 현황 대시보드")
st.markdown("---")

# ── 상단 KPI 카드 ─────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

@st.cache_data(ttl=60)
def fetch_laws():
    try:
        r = requests.get(f"{API_BASE}/laws/", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

@st.cache_data(ttl=60)
def fetch_departments():
    try:
        r = requests.get(f"{API_BASE}/departments/", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

laws = fetch_laws()
departments = fetch_departments()

with col1:
    st.metric("📄 전체 법령 수", len(laws))

with col2:
    summarized = sum(1 for l in laws if l.get("summary"))
    st.metric("✅ 요약 완료", summarized)

with col3:
    unsummarized = len(laws) - summarized
    st.metric("⏳ 요약 대기", unsummarized, delta=f"-{unsummarized}" if unsummarized > 0 else None)

with col4:
    st.metric("🏢 관련 부서 수", len(departments))

st.markdown("---")

# ── 부서별 법령 현황 차트 ──────────────────────────────────────────
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🏢 부서별 법령 현황")
    if departments:
        df_dept = pd.DataFrame([
            {"부서": d["name"], "법령 수": d["law_count"]}
            for d in departments if d["law_count"] > 0
        ])
        if not df_dept.empty:
            st.bar_chart(df_dept.set_index("부서"))
        else:
            st.info("아직 부서에 분류된 법령이 없습니다.")
    else:
        st.warning("부서 데이터를 불러올 수 없습니다.")

with col_right:
    st.subheader("📅 최근 수집 법령")
    if laws:
        df_laws = pd.DataFrame([
            {
                "제목": l["title"],
                "법령번호": l.get("law_number") or "-",
                "개정일": l.get("amended_date") or "-",
                "요약": "✅" if l.get("summary") else "⏳",
            }
            for l in laws[:10]
        ])
        st.dataframe(df_laws, use_container_width=True, hide_index=True)
    else:
        st.warning("법령 데이터를 불러올 수 없습니다. API 서버가 실행 중인지 확인하세요.")

st.markdown("---")

# ── 법령 수집 트리거 ───────────────────────────────────────────────
st.subheader("⚙️ 관리")
col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("🔄 법령 수집 실행", use_container_width=True):
        with st.spinner("수집 중..."):
            try:
                r = requests.post(f"{API_BASE}/laws/collect", timeout=30)
                if r.status_code == 200:
                    data = r.json()
                    st.success(f"✅ {data['message']}")
                    st.cache_data.clear()
                else:
                    st.error("수집 실패")
            except Exception as e:
                st.error(f"연결 오류: {e}")

with col_b:
    if st.button("📊 LangSmith 대시보드 열기", use_container_width=True):
        st.markdown("[🔗 LangSmith 열기](https://smith.langchain.com)", unsafe_allow_html=True)

with col_c:
    if st.button("🔃 화면 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

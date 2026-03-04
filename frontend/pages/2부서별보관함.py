"""
탭 2: 부서별 법령 보관함
- 부서 선택 → 관련 법령 목록
- 법령 클릭 → 요약 상세 보기
"""
import json
import os
import streamlit as st
import requests

API_BASE = "http://localhost:8000/api"
MOCK_FILE = os.path.join(os.path.dirname(__file__), "../../data/departments.json")


def _load_mock() -> dict:
    """가상 데이터 파일 로드"""
    try:
        with open(MOCK_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


@st.cache_data(ttl=120)
def fetch_departments():
    try:
        r = requests.get(f"{API_BASE}/departments/", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data:
                return data, False          # (데이터, 가상여부)
    except Exception:
        pass
    mock = _load_mock().get("GET /api/departments/", [])
    return mock, True                       # 가상 데이터 폴백


@st.cache_data(ttl=60)
def fetch_dept_laws(dept_id: int, is_mock: bool):
    if not is_mock:
        try:
            r = requests.get(f"{API_BASE}/departments/{dept_id}/laws", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
    # 가상 데이터: dept_id 기준으로 필터
    mock_all = _load_mock().get("GET /api/departments/{dept_id}/laws", {})
    mock_laws = mock_all.get("laws", [])
    filtered = [l for l in mock_laws if l.get("id") == dept_id or True]  # 샘플이라 전체 반환
    return {"department": mock_all.get("department", ""), "laws": filtered}


st.title("🗂️ 부서별 보관함")
st.markdown("---")

departments, using_mock = fetch_departments()

if not departments:
    st.warning("부서 데이터를 불러올 수 없습니다. API 서버가 실행 중인지 확인하세요.")
    st.stop()

if using_mock:
    st.info("⚠️ API 서버 미연결 — 가상 데이터로 표시 중입니다.")

# 부서 선택
dept_names = [f"{d['name']} ({d['law_count']}건)" for d in departments]
selected_idx = st.selectbox("🏢 부서 선택", range(len(dept_names)), format_func=lambda i: dept_names[i])
selected_dept = departments[selected_idx]

st.subheader(f"📂 {selected_dept['name']} 관련 법령")

dept_data = fetch_dept_laws(selected_dept["id"], using_mock)
laws = dept_data.get("laws", [])

if not laws:
    st.info(f"{selected_dept['name']}에 분류된 법령이 없습니다.")
else:
    # 검색 필터
    search = st.text_input("🔍 법령 검색", placeholder="법령 제목을 입력하세요...")
    filtered = [l for l in laws if search.lower() in l["title"].lower()] if search else laws

    st.markdown(f"**총 {len(filtered)}건**")

    for law in filtered:
        with st.expander(f"📄 {law['title']} {'✅' if law.get('summary') else '⏳'}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**개정일:** {law.get('amended_date') or '-'}")
                if law.get("summary"):
                    st.markdown("**요약:**")
                    st.info(law["summary"])
                else:
                    st.warning("요약이 아직 생성되지 않았습니다.")
            with col2:
                if st.button("요약 생성", key=f"sum_{law['id']}"):
                    with st.spinner("요약 중..."):
                        try:
                            r = requests.post(f"{API_BASE}/laws/{law['id']}/summarize", timeout=30)
                            if r.status_code == 200:
                                st.success("요약 완료!")
                                st.cache_data.clear()
                                st.rerun()
                        except Exception as e:
                            st.error(f"오류: {e}")

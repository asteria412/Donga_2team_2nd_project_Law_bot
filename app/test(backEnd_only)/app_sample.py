# app/api/app.py

import streamlit as st
import datetime

# ============================================
# 📜 설정 및 공유 변수 (기존 badgeMap 역할)
# ============================================
st.set_page_config(page_title="경영지원본부 법률 포털", layout="wide")

# 부서별 배지 색상 매핑 (CSS 대신 스트림릿 스타일 적용용)
dept_colors = {
    "👥 인사팀": "blue",
    "🏢 총무팀": "green",
    "💼 회계팀": "orange",
    "기타/공통": "gray"
}

# ============================================
# 💡 사이드바 메뉴 (기존 switchTab 로직)
# ============================================
with st.sidebar:
    st.title("메뉴")
    # 기존 data-tab 클릭 이벤트를 스트림릿 라디오 버튼으로 대체
    selected_tab = st.radio(
        "이동할 메뉴를 선택하세요",
        ["🏠 최신 업데이트", "🔍 AI 판례 딥서치"],
        index=0
    )
    
    st.divider()
    
    # 기존 필터 UI (부서 선택, 정렬 등)
    st.subheader("⚙️ 필터 설정")
    selected_dept = st.selectbox("부서 선택", list(dept_colors.keys()))
    sort_order = st.selectbox("정렬 순서", ["최신순", "과거순"])
    display_cnt = st.slider("표시 개수", 5, 20, 10)

# ============================================
# 🚀 메인 화면 그리팅 (기존 switchTab의 titleEl/descEl)
# ============================================
if selected_tab == "🏠 최신 업데이트":
    st.title("좋은 하루되세요, 경영지원본부 임직원 여러분! ☀️")
    st.subheader("핵심 법령의 최신 업데이트 현황을 확인하세요.")
    
    # --------------------------------------------
    # 📑 피드 내용 (기존 fetchLaws 및 카드 UI 렌더링 영역)
    # --------------------------------------------
    st.info(f"현재 {selected_dept}의 최신 법령 {display_cnt}개를 {sort_order}으로 표시 중입니다.")
    
    # 예시 카드 (여기에 데이터가 들어갑니다)
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f":{dept_colors[selected_dept]}[{selected_dept}] **근로기준법 시행령**")
            st.caption("변경: 제3조, 제10조의2 등 | 상세정보는 상세보기를 클릭하세요.")
        with col2:
            # 신구법 직통 링크 적용
            st.link_button("상세보기", "https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=283635#lsRvsDocInfoR")

elif selected_tab == "🔍 AI 판례 딥서치":
    st.title("판례/법령 AI 딥서치 🔍")
    st.subheader("궁금한 법적 키워드를 입력하고 AI와 함께 딥다이브 해보세요.")
    
    # --------------------------------------------
    # 🤖 챗봇 영역 ( Retriever 연결 부위)
    # --------------------------------------------
    query = st.chat_input("질문을 입력하세요 (예: 건설업 임금 지급 책임)")
    if query:
        with st.chat_message("user"):
            st.write(query)
        
        with st.chat_message("assistant"):
            st.write(f"'{query}'에 대한 판례를 분석 중입니다...")
            # 여기서 retriever_instance.invoke(query) 호출!
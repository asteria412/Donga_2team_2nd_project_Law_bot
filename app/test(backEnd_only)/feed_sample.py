# app/api/feed.py

import streamlit as st
import json
import os

# 1. 법령 데이터 불러오기 (JSON 파일 읽기)
def load_law_data(dept_filter, sort_order, display_cnt):
    file_path = "data/raw_data/law_old_new.json" # 약속한 경로
    
    if not os.path.exists(file_path):
        return [], 0

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    laws = data.get("laws", [])
    
    # 필터링 로직 (부서 선택 시)
    if dept_filter != "전체":
        laws = [l for l in laws if l.get("dept") == dept_filter]
        
    # 정렬 로직 (최신순 등)
    reverse_sort = True if sort_order == "최신순" else False
    laws.sort(key=lambda x: x.get("promDt", ""), reverse=reverse_sort)
    
    total_count = len(laws)
    return laws[:display_cnt], total_count

# 2. 상단 요약 카드 렌더링 (기존 updateSummaryCards 역할)
def render_summary_cards(laws):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("최신 업데이트", f"{len(laws)} 건")
    with col2:
        st.metric("검토 필요", f"{int(len(laws) * 0.3)} 건")
    with col3:
        st.metric("AI 분석율", "100 %")

# 3. 법령 피드 렌더링 (기존 renderFeed 역할)
def render_law_feed(laws, total_count):
    if not laws:
        st.warning("해당 조건의 최근 업데이트된 법령이 없습니다.")
        if total_count > 0:
            st.caption(f"(전체 {total_count}건 중 조건에 맞는 데이터 없음)")
        return

    # 카드 목록 출력 (그리드 레이아웃 설정)
    # 스트림릿은 1줄에 2개씩 배치하는게 예뻐요
    cols = st.columns(2) 
    
    for i, law in enumerate(laws):
        with cols[i % 2]: # 좌우 번갈아가며 배치
            with st.container(border=True):
                # 헤더 (배지 영역)
                badge_text = f"✨ [AI] {law.get('dept', '공통')}"
                st.markdown(f"**{badge_text}**   :red[NEW]")
                
                # 제목 및 메타 정보
                st.subheader(law.get("title", "법령명 없음"))
                st.write(f"📅 **공포:** {law.get('promDt')} | **시행:** {law.get('enfDt')}")
                st.write(f"🏢 **주관:** {law.get('agency')}")
                
                # (요약 문구)
                st.caption(f"📝 {law.get('summary', '개정 사항 확인이 필요합니다.')}")
                
                # 하단 버튼 (상세조회 및 AI 퀴즈)
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    # 신구법 직통 링크 
                    #  mst_id(lsiSeq)를 주면 바로 연결
                    link = f"https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq={law.get('mst_id')}#lsRvsDocInfoR"
                    st.link_button("👉 상세 조회", link, use_container_width=True)
                with btn_col2:
                    if st.button(f"🤖 AI 퀴즈", key=f"quiz_{i}", use_container_width=True):
                        st.toast(f"'{law.get('title')}' 관련 퀴즈를 생성합니다!")

# 4. 실제 스트림릿 페이지 적용
def main_feed_page(dept, sort, count):
    st.title("좋은 하루되세요, 경영지원본부 임직원 여러분! ☀️")
    st.write("핵심 법령의 최신 업데이트 현황을 확인하세요.")
    
    # 데이터 로드
    laws, total = load_law_data(dept, sort, count)
    
    # 요약 카드 표시
    render_summary_cards(laws)
    st.divider()
    
    # 피드 표시
    render_law_feed(laws, total)
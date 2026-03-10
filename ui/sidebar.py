""" ui/sidebar.py
[사이드바 내비게이션] 무한개발공사의 'raw_bot' 프로젝트 메인 메뉴와 필터링 옵션을 관리하는 파일입니다.
'무한raw봇' 챗봇 및 실시간 법령 피드 메뉴 전환을 담당하며, 부서별 필터 및 정렬 기준 등 세부 설정값을 통합 제어하는 인터페이스를 제공합니다. """

import streamlit as st

def render_sidebar():
    # Logo Section
    logo_path = "assets/logo.png"
    
    st.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
    st.image(logo_path, use_container_width=True)
    st.markdown("""
        <div style="text-align: center;">
            <span style="color: #1a73e8; font-size: 24px; font-weight: 800; letter-spacing: -1px;">무한개발공사</span>
            <p style="color:#65676b; font-size:14px; margin-top:0px; font-weight:500;">경영지원본부 Legal Service</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    menu_options = ["📜 실시간 법령 피드", "💬 AI 사내규정 챗봇"]
    selected_page = st.radio("MAIN MENU", menu_options, label_visibility="collapsed")

    st.write("")
    st.markdown("---")
    st.caption("타겟 부서 필터")
    selected_dept = st.radio("부서 선택",
        ["전체 (핵심 12법령)", "인사팀", "총무팀", "재무팀"], label_visibility="collapsed")

    st.write("")
    st.caption("상세 설정")
    sort_opt = st.selectbox("정렬 기준", ["공포일자 (최신순)", "시행일자 (최신순)"])
    limit = st.selectbox("출력 개수", [10, 20, 50, 100], index=1)

    return selected_page, selected_dept, sort_opt, limit

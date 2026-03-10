import streamlit as st

def render_sidebar():
    st.markdown("""
    <div class="sidebar-logo" style="padding-left: 0px; margin-left: -6px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 35px;">🏢</span>
            <span style="color: #4c6ef5; font-size: 30px; font-weight: 800; letter-spacing: -2px;">
                무한상사
            </span>
        </div>
        <p style="color:#868e96; font-size:18px; padding-left:45px; margin-top:5px; font-weight:500;">
            경영지원본부
        </p>
    </div>
    """, unsafe_allow_html=True)

    menu_options = ["📜 실시간 법령 피드", "💬 AI 법무 챗봇"]
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

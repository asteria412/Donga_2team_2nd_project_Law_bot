import streamlit as st
from ui.quiz_modal import quiz_modal

def render_law_card(law):
    p = _fmt(law["p_dt"])
    e = _fmt(law["e_dt"])
    summary_html = f'<div class="law-info" style="color:#228be6;font-weight:500;margin-top:5px;">{law["summary"]}</div>' if law.get("summary") else ""

    html = (
        f'<div class="law-card"><div class="law-card-content">'
        f'<div class="law-badge-area"><span class="law-dept-badge">{law["dept"]}</span>'
        f'<span class="law-new-badge">NEW</span></div>'
        f'<div class="law-title">{law["title"]}</div>'
        f'<div class="law-info">공포: {p} | 시행: {e}</div>'
        f'<div class="law-info">주관: {law["agency"]}</div>'
        f'{summary_html}'
        '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("👉 상세 정보(신구법)",
            f"https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq={law['mst_id']}&viewCls=lsOldAndNew",
            use_container_width=True)
    with col2:
        if st.button("🤖 AI 퀴즈", key=f"quiz{law['mst_id']}", use_container_width=True):
            quiz_modal(law)

def _fmt(raw):
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}" if len(raw)==8 else raw

import streamlit as st

def render_summary_cards(count):
    html = f"""
    <div class="summary-card-container">
        <div class="summary-card">
            <div class="summary-icon" style="background:#e7f5ff; color:#228be6;">📝</div>
            <div>
                <div class="sum-label">최근 90일 법령 개정</div>
                <div class="sum-val">{count} <span style='font-size:18px; font-weight:400;'>건</span></div>
            </div>
        </div>
        <div class="summary-card">
            <div class="summary-icon" style="background:#f3f0ff; color:#7950f2;">👥</div>
            <div>
                <div class="sum-label">부서별 태깅 완료</div>
                <div class="sum-val">100 <span style='font-size:18px; font-weight:400;'>%</span></div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

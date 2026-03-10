""" ui/summary_cards.py
[요약 대시보드 카드] 무한개발공사의 'raw_bot' 프로젝트 메인 화면 상단에 통계 정보를 렌더링하는 파일입니다.
최근 90일간 수집된 법령 개정 건수와 부서별 태깅 현황 등 주요 지표를 시각적인 요약 카드 형태로 구성하여 '무한raw봇' 사용자에게 제공합니다. """

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

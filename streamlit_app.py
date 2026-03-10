""" streamlit_app.py
[메인 엔트리 포인트] 무한상사의 'raw_bot' 서비스를 구동하는 통합 실행 파일입니다.
전체 UI 스타일을 적용하고 사이드바 내비게이션을 통해 '실시간 법령 피드'와 '무한raw봇' 챗봇 페이지 간의 화면 전환을 제어하는 오케스트레이터 역할을 수행합니다. """

import streamlit as st
from style.base_style import BASE_STYLE

from ui.sidebar import render_sidebar
from ui.feed_page import render_feed_page
from ui.chatbot_page import render_chatbot_page

st.set_page_config(
    page_title="무한상사 raw-bot",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(BASE_STYLE, unsafe_allow_html=True)

with st.sidebar:
    selected_page, selected_dept, sort_opt, limit = render_sidebar()

if "실시간 법령 피드" in selected_page:
    render_feed_page(selected_dept, sort_opt, limit)
else:
    render_chatbot_page()

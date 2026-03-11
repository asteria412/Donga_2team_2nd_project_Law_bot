""" ui/feed_page.py
[법령 피드 페이지] 무한개발공사의 'raw_bot' 프로젝트에서 외부 최신 법령 개정 소식을 보여주는 화면입니다.
경영지원본부 임직원들을 위해 최근 90일간의 법령 업데이트 데이터를 수집하여 요약 카드와 리스트 형태로 시각화하여 제공합니다. """

import streamlit as st
from logic.law_api import get_laws_sync
from ui.law_card import render_law_card
from ui.summary_cards import render_summary_cards

def render_feed_page(selected_dept, sort_opt, limit):
    st.markdown('<h1 style="font-weight: 800; letter-spacing: -1.5px;">⚖️ 실시간 법령 피드</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color:#65676b; font-size:1.1rem; margin-top:-10px; font-weight:500;'>무한개발공사 임직원 여러분, 안녕하십니까? 최신 법령 개정 소식을 전해드립니다.</p>", unsafe_allow_html=True)

    laws = get_laws_sync(selected_dept, limit)

    render_summary_cards(len(laws))
    st.markdown(f"#### 최근 업데이트 리스트({limit}개)")

    cols = st.columns(2, gap="small")
    for i, law in enumerate(laws[:limit]):
        with cols[i % 2]:
            render_law_card(law)

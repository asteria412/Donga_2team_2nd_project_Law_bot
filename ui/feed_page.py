import streamlit as st
from logic.law_api import get_laws_sync
from ui.law_card import render_law_card
from ui.summary_cards import render_summary_cards

def render_feed_page(selected_dept, sort_opt, limit):
    st.title("⚖️ 무한상사 Raw-bot")
    st.markdown("### 좋은 하루되세요, 경영지원본부 임직원 여러분! 🌞")
    st.markdown("<p style='color:#868e96;margin-top:-10px;'>최근 90일간 업데이트된 핵심 법령을 확인하세요.</p>",unsafe_allow_html=True)

    laws = get_laws_sync(selected_dept, limit)

    render_summary_cards(len(laws))
    st.markdown(f"#### 최근 업데이트 리스트({limit}개)")

    cols = st.columns(2)
    for i, law in enumerate(laws[:limit]):
        with cols[i % 2]:
            render_law_card(law)

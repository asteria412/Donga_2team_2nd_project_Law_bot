import streamlit as st
from style.base_style import BASE_STYLE

from ui.sidebar import render_sidebar
from ui.feed_page import render_feed_page
from ui.chatbot_page import render_chatbot_page
from dotenv import load_dotenv

load_dotenv()

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
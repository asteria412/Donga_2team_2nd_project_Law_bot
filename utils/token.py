import streamlit as st

def update_token_usage(usage_obj):
    """
    OpenAI의 usage 객체를 받아 Streamlit 세션에 누적합니다.
    """
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
        st.session_state.prompt_tokens = 0
        st.session_state.completion_tokens = 0

    st.session_state.total_tokens += usage_obj.total_tokens
    st.session_state.prompt_tokens += usage_obj.prompt_tokens
    st.session_state.completion_tokens += usage_obj.completion_tokens
    print(f"Updated token usage: Total={st.session_state.total_tokens}, Prompt={st.session_state.prompt_tokens}, Completion={st.session_state.completion_tokens}")
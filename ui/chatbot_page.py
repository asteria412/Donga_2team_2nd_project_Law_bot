""" ui/chatbot_page.py
[챗봇 인터페이스] 무한상사의 'raw_bot' 프로젝트에서 '무한raw봇'과의 대화 화면을 렌더링하는 파일입니다.
사용자가 입력한 질문을 RAG 엔진에 전달하여 사내 규정 답변을 받아오고, 채팅 형식의 UI로 시각화하여 제공합니다. """

import streamlit as st
from logic.rag_engine import search as rag_search
from logic.summarizer import generate_quiz_from_ai
from openai import OpenAI

def render_chatbot_page():
    st.markdown("### 💬 AI 법무 챗봇 '도비'")
    st.markdown("<p style='color:#868e96;margin-top:-10px;'>사내 규정 및 법률 관련 궁금한 점을 물어보세요.</p>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role":"assistant","content":"안녕하세요! 경영지원본부 AI 도비입니다. 무엇을 도와드릴까요?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("질문을 입력해주세요 (예: 연차 휴가 규정 알려줘)"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("규정을 분석 중입니다..."):
                results = rag_search(prompt, top_k=3)
                context = "\n".join(r['text'] for r in results) if results else "관련 규정을 찾을 수 없습니다."

                client = OpenAI()
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "사내 규정 전문가 AI 도비입니다."},
                        {"role": "user", "content": f"[규정]\n{context}\n\n[질문]\n{prompt}"}
                    ]
                )
                ans = res.choices[0].message.content

            st.markdown(ans)
            st.session_state.messages.append({"role":"assistant","content":ans})

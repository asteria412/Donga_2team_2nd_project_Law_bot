""" ui/chatbot_page.py
[챗봇 인터페이스] 무한개발공사의 'Law_bot' 프로젝트에서 '무한Law봇'과의 대화 화면을 렌더링하는 파일입니다.
사용자가 입력한 질문을 RAG 엔진에 전달하여 사내 규정 답변을 받아오고, 채팅 형식의 UI로 시각화하여 제공합니다. """

import streamlit as st
from logic.rag_engine import search as rag_search
from logic.summarizer import generate_quiz_from_ai
from openai import OpenAI
from utils.token import update_token_usage

def render_chatbot_page():
    st.markdown("### 💬 AI 사내규정 챗봇 '무한Law봇'")
    st.markdown("<p style='color:#868e96;margin-top:-10px;'>무한개발공사 사내 규정에 대해 무엇이든 물어보세요.</p>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role":"assistant","content":"안녕하세요! 무한개발공사 규정 안내 전문가, AI 무한Law봇입니다. 무엇을 도와드릴까요?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("질문을 입력해주세요 (예: 연차 휴가 규정 알려줘)"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("규정을 분석 중입니다..."):
                results = rag_search(prompt, top_k=3)
                #각 청크 앞에 문서명을 태그처럼 붙여줌
                context = ""
                for r in results:
                    context += f"[{r['source']}] {r['text']}\n---\n" if results else "관련 규정을 찾을 수 없습니다."

                client = OpenAI()
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": (
                                "당신은 무한개발공사의 사내 규정 전문가입니다. "
                                "제공된 [규정] 내용에 기반하여 본론의 핵심만 답변하세요. "
                                "답변의 본문 내용에는 출처를 명시하지 않아야 합니다"
                                "반드시 답변 하단에 해당 내용의 출처인 명칭과 조항을 명시하세요."
                                "(예:📍근거 규정:취업규정 제26조,부패신고 처리 및 신고자 보호 등에 관한 운영 내규 제17조)"
                                "제공된 규정에서 가장 연관성 높은 내용을 찾아 안내하고 근거규정이 없거나 완전히 무관한 내용일 때만"
                                "'해당 내용은 현재 규정에서 찾을 수 없습니다.'라고 답변하고 출처를 제외하세요.")},
                        {"role": "user", "content": f"[규정]\n{context}\n\n[질문]\n{prompt}"}
                    ]
                )
                update_token_usage(res.usage)
                ans = res.choices[0].message.content

            st.markdown(ans)
            st.session_state.messages.append({"role":"assistant","content":ans})
            st.rerun()

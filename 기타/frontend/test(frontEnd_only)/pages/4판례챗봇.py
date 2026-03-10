"""
탭 4: 판례 챗봇 - RAG 기반 법령/판례 질의응답
"""
import streamlit as st
import requests

API_BASE = "http://localhost:8000/api"

st.title("💬 판례 챗봇")
st.markdown("수집된 법령 기반 AI 질의응답 (RAG)")
st.markdown("---")

# 채팅 히스토리 초기화
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "안녕하세요! 법령 및 판례에 대해 무엇이든 질문해주세요. 수집된 법령 데이터를 기반으로 답변드립니다."}
    ]

# 기존 메시지 렌더링
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
if prompt := st.chat_input("법령 관련 질문을 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("법령 데이터를 검색 중..."):
            try:
                r = requests.post(
                    f"{API_BASE}/rag/answer",
                    json={"question": prompt},
                    timeout=60,
                )
                if r.status_code == 200:
                    answer = r.json().get("answer", "답변을 생성할 수 없습니다.")
                else:
                    # API 미구현 시 폴백: RAG retriever 직접 호출
                    answer = _direct_rag_answer(prompt)
            except Exception:
                answer = _direct_rag_answer(prompt)

        st.markdown(answer)
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})


def _direct_rag_answer(question: str) -> str:
    """API 서버 없이 직접 RAG retriever 호출 (폴백)"""
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
        from app.rag.retriever import LawRetriever
        retriever = LawRetriever()
        return retriever.answer(question)
    except Exception as e:
        return f"오류가 발생했습니다: {e}\n\nAPI 서버(uvicorn)가 실행 중인지 확인해주세요."


# 사이드바 - 관련 법령 검색
with st.sidebar:
    st.subheader("🔍 관련 법령 검색")
    if st.session_state.chat_messages:
        last_user = next(
            (m["content"] for m in reversed(st.session_state.chat_messages) if m["role"] == "user"),
            None,
        )
        if last_user:
            try:
                r = requests.get(f"{API_BASE}/laws/?search={last_user[:20]}", timeout=5)
                if r.status_code == 200:
                    related = r.json()[:3]
                    for law in related:
                        st.markdown(f"📄 **{law['title']}**")
                        if law.get("summary"):
                            st.caption(law["summary"][:100] + "...")
                        st.markdown("---")
            except Exception:
                pass

    if st.button("🗑️ 대화 초기화"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "대화가 초기화되었습니다. 새로운 질문을 입력해주세요."}
        ]
        st.rerun()

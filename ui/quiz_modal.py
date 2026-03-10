""" ui/quiz_modal.py
[AI 실무 퀴즈 모달] 무한상사의 'raw_bot' 프로젝트에서 특정 법령에 대한 실무 퀴즈 화면을 띄워주는 컴포넌트입니다.
'무한raw봇'이 생성한 시나리오 기반의 퀴즈를 사용자에게 보여주고, 정답 확인 및 전문가의 해설을 인터랙티브한 팝업창(Dialog) 형태로 제공합니다. """

import streamlit as st
from logic.summarizer import generate_quiz_from_ai

@st.dialog("🤖 AI 실무 퀴즈")
def quiz_modal(law):
    # 세션 상태 초기화 (해당 법령의 퀴즈가 없거나 다른 법령이면 새로 생성)
    if "quiz" not in st.session_state or st.session_state.get("quiz_mst_id") != law['mst_id']:
        with st.spinner("AI가 퀴즈를 생성하고 있습니다..."):
            q = generate_quiz_from_ai({
                'law_name': law['title'],
                'enf_dt': law['e_dt'],
                'mst_id': law['mst_id']
            })
            if q:
                st.session_state.quiz = q
                st.session_state.quiz_mst_id = law['mst_id']
                st.session_state.quiz_submitted = False
            else:
                st.error("퀴즈 생성에 실패했습니다.")
                return

    q = st.session_state.quiz

    st.subheader(f"Q. {q['question']}")
    st.write("")
    
    # 정답 제출 전후에 따라 라디오 버튼 비활성화 여부 결정
    choice = st.radio(
        "보기에서 정답을 골라보세요:", 
        q['options'], 
        key="quiz_choice",
        disabled=st.session_state.quiz_submitted
    )

    if not st.session_state.quiz_submitted:
        if st.button("정답 확인", type="primary", use_container_width=True):
            st.session_state.quiz_submitted = True
            st.rerun()
    
    # 결과 표시
    if st.session_state.quiz_submitted:
        if choice == q['answer']:
            st.success("🎉 정답입니다!")
        else:
            st.error(f"❌ 아쉽네요. 정답은 {q['answer']} 입니다.")
        
        st.info(f"💡 해설\n{q['explanation']}")
        
        if st.button("닫기", use_container_width=True):
            st.session_state[f"show_quiz_{law['mst_id']}"] = False
            st.rerun()

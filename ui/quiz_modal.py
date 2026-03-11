""" ui/quiz_modal.py
[AI 실무 퀴즈 모달] 무한개발공사의 'raw_bot' 프로젝트에서 특정 법령에 대한 실무 퀴즈 화면을 띄워주는 컴포넌트입니다.
'무한raw봇'이 생성한 시나리오 기반의 퀴즈를 사용자에게 보여주고, 정답 확인 및 전문가의 해설을 인터랙티브한 팝업창(Dialog) 형태로 제공합니다. """

import streamlit as st
from logic.summarizer import generate_quiz_from_ai

@st.dialog("🤖 AI 실무 퀴즈")
def quiz_modal(law):
    # 세션 상태 초기화
    if "quiz_idx" not in st.session_state or st.session_state.get("quiz_mst_id") != law['mst_id']:
        st.session_state.quiz_idx = 0
        st.session_state.quiz_mst_id = law['mst_id']
        st.session_state.quiz_submitted = False
        st.session_state.quiz_data = None

    # 현재 인덱스에 해당하는 퀴즈 로드
    current_idx = st.session_state.quiz_idx
    
    # 퀴즈 데이터가 없거나 인덱스가 바뀌었을 때 생성
    if st.session_state.quiz_data is None:
        with st.spinner("AI가 실무형 퀴즈를 생성하고 있습니다..."):
            quizzes = generate_quiz_from_ai({
                'law_name': law['title'],
                'enf_dt': law['e_dt'],
                'mst_id': law['mst_id']
            }, count=3) # 한 번에 3문제 요청
            
            if quizzes:
                st.session_state.quiz_data = quizzes
            else:
                st.error("퀴즈 생성에 실패했습니다.")
                return

    # 현재 문제 가져오기 (리스트 형태이므로 인덱스로 접근)
    quizzes = st.session_state.quiz_data
    if current_idx >= len(quizzes):
        st.success("🏁 모든 문제를 준비했습니다! (문제가 더 필요하면 나중에 다시 시도해주세요)")
        if st.button("닫기", use_container_width=True):
            st.session_state.active_quiz_id = None
            st.rerun()
        return

    q = quizzes[current_idx]

    st.subheader(f"Q{current_idx + 1}. {q['question']}")
    st.write("")
    
    # 라디오 버튼 - 제출 후에 선택값이 고정되도록 키를 인덱스별로 분리
    choice = st.radio(
        "보기에서 정답을 골라보세요:", 
        q['options'], 
        key=f"quiz_choice_{law['mst_id']}_{current_idx}",
        disabled=st.session_state.quiz_submitted
    )

    if not st.session_state.quiz_submitted:
        if st.button("정답 확인", type="primary", use_container_width=True):
            st.session_state.quiz_submitted = True
            st.rerun()
    
    if st.session_state.quiz_submitted:
        is_correct = False
        # 1. 완전 일치 비교
        if choice == q['answer']:
            is_correct = True
        # 2. "보기N" 형태의 AI 답변 방어 로직
        elif q['answer'].startswith("보기") and q['answer'][2:].isdigit():
            ans_idx = int(q['answer'][2:]) - 1
            if 0 <= ans_idx < len(q['options']) and choice == q['options'][ans_idx]:
                is_correct = True

        if is_correct:
            st.success("🎉 정답입니다!")
        else:
            # 정답 가이드도 똑똑하게 표시
            display_answer = q['answer']
            if q['answer'].startswith("보기") and q['answer'][2:].isdigit():
                ans_idx = int(q['answer'][2:]) - 1
                if 0 <= ans_idx < len(q['options']):
                    display_answer = q['options'][ans_idx]
            
            st.error(f"❌ 아쉽네요. 정답은 [{display_answer}] 입니다.")
        
        st.info(f"💡 해설\n{q['explanation']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if current_idx + 1 < len(quizzes):
                if st.button("다음 문제 ➡️", use_container_width=True):
                    st.session_state.quiz_idx += 1
                    st.session_state.quiz_submitted = False
                    st.rerun()
            else:
                st.write("마지막 문제입니다.")
        with col2:
            if st.button("닫기", use_container_width=True):
                st.session_state.active_quiz_id = None
                st.rerun()

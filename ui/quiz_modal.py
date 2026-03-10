import streamlit as st
from logic.summarizer import generate_quiz_from_ai

@st.dialog("🤖 AI 실무 퀴즈")
def quiz_modal(law):
    with st.spinner("AI가 퀴즈를 생성하고 있습니다..."):
        q = generate_quiz_from_ai({
            'law_name': law['title'],
            'enf_dt': law['e_dt'],
            'mst_id': law['mst_id']
        })

    if q:
        st.subheader(f"Q. {q['question']}")
        st.write("")
        choice = st.radio("보기에서 정답을 골라보세요:", q['options'])

        if st.button("정답 확인", type="primary", use_container_width=True):
            if choice == q['answer']:
                st.success("🎉 정답입니다!")
            else:
                st.error(f"❌ 아쉽네요. 정답은 {q['answer']} 입니다.")
            st.info(f"💡 해설\n{q['explanation']}")
    else:
        st.error("퀴즈 생성에 실패했습니다.")

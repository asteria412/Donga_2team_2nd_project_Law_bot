"""
탭 5: 법령 숙지 퀴즈
"""
import streamlit as st
import requests

API_BASE = "http://localhost:8000/api"

st.title("📝 숙지 퀴즈")
st.markdown("법령 내용을 기반으로 생성된 4지선다 퀴즈")
st.markdown("---")

# 세션 상태
if "quiz_list" not in st.session_state:
    st.session_state.quiz_list = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False


@st.cache_data(ttl=60)
def fetch_laws():
    try:
        r = requests.get(f"{API_BASE}/laws/", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


laws = fetch_laws()

col1, col2 = st.columns([2, 1])

with col1:
    if laws:
        law_options = {f"[{l['id']}] {l['title']}": l["id"] for l in laws}
        selected_name = st.selectbox("📄 퀴즈 생성할 법령 선택", list(law_options.keys()))
        selected_id = law_options[selected_name]
    else:
        st.warning("법령이 없습니다.")
        selected_id = None

with col2:
    quiz_count = st.number_input("문제 수", min_value=1, max_value=10, value=3)
    difficulty = st.selectbox("난이도", ["easy", "medium", "hard"], index=1)

col_gen, col_load = st.columns(2)

with col_gen:
    if st.button("🤖 AI 퀴즈 생성", type="primary", use_container_width=True, disabled=not selected_id):
        with st.spinner("퀴즈를 생성 중입니다..."):
            try:
                r = requests.post(
                    f"{API_BASE}/quiz/generate",
                    json={"law_id": selected_id, "count": quiz_count, "difficulty": difficulty},
                    timeout=60,
                )
                if r.status_code == 200:
                    st.session_state.quiz_list = r.json().get("quizzes", [])
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.success(f"✅ {len(st.session_state.quiz_list)}개 퀴즈 생성 완료!")
                else:
                    st.error("퀴즈 생성에 실패했습니다.")
            except Exception as e:
                st.error(f"연결 오류: {e}")

with col_load:
    if st.button("📂 저장된 퀴즈 불러오기", use_container_width=True, disabled=not selected_id):
        try:
            r = requests.get(f"{API_BASE}/quiz/{selected_id}?limit={quiz_count}", timeout=5)
            if r.status_code == 200:
                st.session_state.quiz_list = r.json().get("quizzes", [])
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                if st.session_state.quiz_list:
                    st.success(f"✅ {len(st.session_state.quiz_list)}개 불러왔습니다.")
                else:
                    st.info("저장된 퀴즈가 없습니다. 먼저 생성해주세요.")
        except Exception as e:
            st.error(f"오류: {e}")

st.markdown("---")

# 퀴즈 렌더링
if st.session_state.quiz_list:
    st.subheader(f"📋 퀴즈 ({len(st.session_state.quiz_list)}문제)")

    for i, quiz in enumerate(st.session_state.quiz_list):
        st.markdown(f"**Q{i+1}. {quiz['question']}**")

        if not st.session_state.quiz_submitted:
            answer = st.radio(
                f"",
                options=quiz["options"],
                key=f"q_{i}",
                index=None,
                label_visibility="collapsed",
            )
            if answer is not None:
                st.session_state.quiz_answers[i] = quiz["options"].index(answer)
        else:
            # 제출 후: 정오 표시
            user_ans = st.session_state.quiz_answers.get(i)
            correct_ans = quiz["answer_index"]
            for j, opt in enumerate(quiz["options"]):
                if j == correct_ans:
                    st.markdown(f"✅ {opt} ← **정답**")
                elif j == user_ans:
                    st.markdown(f"❌ {opt} ← 내 선택")
                else:
                    st.markdown(f"　　{opt}")
            if quiz.get("explanation"):
                st.info(f"💡 {quiz['explanation']}")

        st.markdown("---")

    if not st.session_state.quiz_submitted:
        if st.button("📤 제출하기", type="primary", use_container_width=True):
            if len(st.session_state.quiz_answers) < len(st.session_state.quiz_list):
                st.warning("모든 문제에 답을 선택해주세요.")
            else:
                st.session_state.quiz_submitted = True
                st.rerun()
    else:
        # 점수 표시
        correct = sum(
            1 for i, q in enumerate(st.session_state.quiz_list)
            if st.session_state.quiz_answers.get(i) == q["answer_index"]
        )
        total = len(st.session_state.quiz_list)
        score_pct = int(correct / total * 100)

        if score_pct == 100:
            st.balloons()
            st.success(f"🎉 완벽! {correct}/{total} ({score_pct}점)")
        elif score_pct >= 60:
            st.success(f"👍 통과! {correct}/{total} ({score_pct}점)")
        else:
            st.error(f"😢 재도전 필요 {correct}/{total} ({score_pct}점)")

        if st.button("🔄 다시 풀기", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()

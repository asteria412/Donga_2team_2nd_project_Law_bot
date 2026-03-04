"""
탭 3: 리포트 센터 - before/after 변경 비교
"""
import streamlit as st
import requests

API_BASE = "http://localhost:8000/api"

st.title("📋 리포트 센터")
st.markdown("before / after 법령 비교 분석 리포트")
st.markdown("---")

tab1, tab2 = st.tabs(["🔄 변경 비교", "📜 변경 이력"])

with tab1:
    st.subheader("법령 변경 전·후 비교")

    @st.cache_data(ttl=60)
    def fetch_laws():
        try:
            r = requests.get(f"{API_BASE}/laws/", timeout=5)
            return r.json() if r.status_code == 200 else []
        except Exception:
            return []

    laws = fetch_laws()

    if not laws:
        st.warning("법령 데이터가 없습니다.")
    else:
        law_options = {f"[{l['id']}] {l['title']}": l["id"] for l in laws}
        selected_name = st.selectbox("📄 비교할 법령 선택", list(law_options.keys()))
        selected_id = law_options[selected_name]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📌 이전 법령 (현재 저장본)**")
            law_detail = next((l for l in laws if l["id"] == selected_id), None)
            before_text = st.text_area(
                "이전 내용 (자동 로드)",
                value=law_detail.get("summary", "") if law_detail else "",
                height=250,
                disabled=True,
            )

        with col2:
            st.markdown("**✏️ 개정된 법령 내용 입력**")
            after_text = st.text_area("개정 내용을 붙여넣으세요", height=250, placeholder="개정 법령 전문을 입력하세요...")

        if st.button("🔍 변경 비교 분석 실행", type="primary", use_container_width=True):
            if not after_text.strip():
                st.error("개정 내용을 입력해주세요.")
            else:
                with st.spinner("AI가 변경 사항을 분석 중입니다..."):
                    try:
                        r = requests.post(
                            f"{API_BASE}/reports/compare",
                            json={"law_id": selected_id, "new_content": after_text},
                            timeout=60,
                        )
                        if r.status_code == 200:
                            result = r.json()
                            st.markdown("---")
                            st.subheader("📊 분석 결과")
                            if result.get("has_changes"):
                                st.success("변경 사항이 감지되었습니다.")
                                st.markdown(result.get("analysis", ""))
                                if result.get("history_id"):
                                    st.info(f"이력 ID {result['history_id']}로 저장되었습니다.")
                            else:
                                st.info("변경 사항이 없습니다.")
                    except Exception as e:
                        st.error(f"연결 오류: {e}")

with tab2:
    st.subheader("📜 법령 변경 이력")

    laws = fetch_laws()
    if laws:
        law_options = {f"[{l['id']}] {l['title']}": l["id"] for l in laws}
        selected_name = st.selectbox("법령 선택", list(law_options.keys()), key="hist_select")
        selected_id = law_options[selected_name]

        try:
            r = requests.get(f"{API_BASE}/reports/history/{selected_id}", timeout=5)
            if r.status_code == 200:
                histories = r.json().get("histories", [])
                if not histories:
                    st.info("아직 변경 이력이 없습니다.")
                else:
                    for h in histories:
                        with st.expander(f"v{h['version']} | {h['change_type']} | {h['changed_at'][:10]}"):
                            if st.button("상세 보기", key=f"hist_{h['id']}"):
                                detail_r = requests.get(
                                    f"{API_BASE}/reports/history/{selected_id}/{h['version']}", timeout=5
                                )
                                if detail_r.status_code == 200:
                                    d = detail_r.json()
                                    c1, c2 = st.columns(2)
                                    with c1:
                                        st.markdown("**이전**")
                                        st.text_area("", value=d.get("content_before", "")[:1000], height=200, disabled=True)
                                    with c2:
                                        st.markdown("**이후**")
                                        st.text_area("", value=d.get("content_after", "")[:1000], height=200, disabled=True)
        except Exception as e:
            st.error(f"이력 조회 실패: {e}")

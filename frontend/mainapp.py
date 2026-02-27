import streamlit as st


st.set_page_config(
    page_title="법령 기반 리스크 관리 플랫폼",
    layout="wide",
)


def main() -> None:
    st.title("법령 기반 리스크 관리 플랫폼")
    st.markdown(
        """
        왼쪽 사이드바의 페이지를 선택해 각 기능을 사용할 수 있습니다.

        - 리스크 현황
        - 부서별 보관함
        - 리포트 센터
        - 판례 챗봇
        """
    )


if __name__ == "__main__":
    main()

# C:\Users\Donga\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run streamlit_app.py
import streamlit as st
import datetime
import requests
import xml.etree.ElementTree as ET
import sys
import os
import time
from dotenv import load_dotenv

# 1. 경로 설정 및 로직 불러오기
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

try:
    from app.agent.tagger import predict_department_with_ai
    from app.agent.rag_engine import search as rag_search
    from app.agent.summarizer import generate_quiz_from_ai
except ImportError:
    st.error("기존 에이전트 파일을 찾을 수 없습니다.")

# 2. 설정
API_KEY = os.getenv("LAW_API_KEY")
BASE_URL_LAW = 'https://www.law.go.kr/DRF/lawSearch.do'
BASE_URL_SERVICE = 'https://www.law.go.kr/DRF/lawService.do'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

# 3. 페이지 설정
st.set_page_config(
    page_title="무한상사 raw-bot",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 4. 전체 스타일 시트 (기존 웹 디자인 이식)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        background-color: #f8f9fa;
    }

    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #eee;
        padding-top: 20px;
    }
    .sidebar-logo {
        padding: 0 20px 20px 20px;
        margin-bottom: 20px;
    }
    .sidebar-menu-item {
        padding: 12px 20px;
        margin: 4px 10px;
        border-radius: 8px;
        color: #555;
        font-weight: 500;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .sidebar-menu-item.active {
        background-color: #4c6ef5;
        color: white;
    }

    /* 🌟 라디오 버튼(메뉴) 간격 및 스타일 커스텀 (끝판왕 버전) */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 20px !important; /* 항목 사이의 간격을 40px로 강제 지정 */
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        font-size: 18px !important;
        font-weight: 500 !important;
        color: #495057 !important;
    }
    
    /* 요약 카드 스타일 */
    .summary-card-container {
        display: flex;
        gap: 24px;
        margin-bottom: 30px;
    }
    .summary-card {
        flex: 1;
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        display: flex;
        align-items: center;
        gap: 20px;
        border: 1px solid #f1f3f5;
    }
    .summary-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    .sum-val {
        font-size: 28px;
        font-weight: 700;
        color: #212529;
    }
    .sum-label {
        font-size: 14px;
        color: #868e96;
        margin-bottom: 4px;
    }

    /* 법령 리스트 카드 */
    .law-card {
        background: white;
        border-radius: 20px;
        border: 1px solid #f1f3f5;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
        margin-bottom: 20px;
        overflow: hidden;
    }
    .law-card-content {
        padding: 30px;
        height: 240px; /* 🌟 높이를 280px로 완전히 고정! */
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .law-badge-area {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
    }
    .law-dept-badge {
        background: #f1f3f5;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 13px;
        color: #495057;
        font-weight: 500;
    }
    .law-new-badge {
        background: #ebfbee;
        color: #40c057;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
    }
    .law-title {
        font-size: 20px;
        font-weight: 700;
        color: #212529;
        margin-bottom: 15px;
        line-height: 1.4;
    }
    .law-info {
        font-size: 14px;
        color: #868e96;
        margin-bottom: 8px;
    }
    
    /* 카드 하단 액션 버튼 영역 */
    .law-actions {
        background: #fcfdfe;
        border-top: 1px solid #f1f3f5;
        padding: 20px 30px;
        display: flex;
        gap: 15px;
    }
    .btn-detail {
        color: #4c6ef5;
        font-weight: 600;
        font-size: 15px;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 5. 사이드바 (무한상사 전용 테마 및 기능 연결)
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo" style="padding-left: 0px; margin-left: -6px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 35px;">🏢</span>
            <span style="color: #4c6ef5; font-size: 30px; font-weight: 800; letter-spacing: -2px;">무한상사</span>
        </div>
        <p style="color: #868e96; font-size: 18px; margin-top: 5px; padding-left: 45px; font-weight: 500;">경영지원본부</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 🌟 실제 작동하는 메뉴로 교체!
    menu_options = ["📜 실시간 법령 피드", "💬 AI 법무 챗봇"]
    selected_page = st.radio("MAIN MENU", menu_options, label_visibility="collapsed")
    
    st.write("")
    st.markdown("---")
    st.caption("타겟 부서 필터")
    selected_dept = st.radio("부서 선택", ["전체 (핵심 12법령)", "인사팀", "총무팀", "재무팀"], label_visibility="collapsed")
    
    st.write("")
    st.caption("상세 설정")
    sort_opt = st.selectbox("정렬 기준", ["공포일자 (최신순)", "시행일자 (최신순)"])
    limit = st.selectbox("출력 개수", [10, 20, 50, 100], index=1)

# 6. 데이터 로직 (Sync with api_server.py)
import re  # 정규식: 조문제목 추출에 사용

def get_law_change_summary(mst_id, session):
    """법령 상세 API를 통해 첫 번째 개정 조문 제목을 추출합니다."""
    try:
        params = {
            'OC': API_KEY,
            'target': 'oldAndNew',
            'MST': mst_id,
            'type': 'XML'
        }
        res = session.get(BASE_URL_SERVICE, params=params, timeout=10)
        res.raise_for_status()
        
        root = ET.fromstring(res.text)
        
        # <신조문목록> 아래 <조문> 태그들을 순회
        # 조문 내용은 CDATA 텍스트로 존재하며, "제N조(제목)" 형태의 패턴을 찾음
        pattern = re.compile(r'제\d+조\(.*?\)')
        
        # 신조문목록 내 조문 탐색
        for elem in root.iter():
            if elem.text:
                match = pattern.search(elem.text)
                if match:
                    return f"📍 {match.group()} 등 개정"
        
        return ""
    except Exception:
        return ""

def get_laws_sync(dept, count):
    DEPT_KEYWORDS = {
        "인사팀": ["근로기준법", "남녀고용평등", "산업안전보건법", "최저임금법", "근로자퇴직급여", "파견근로자"],
        "총무팀": ["개인정보 보호법", "상법", "부정청탁", "독점규제 및 공정거래", "하도급거래"],
        "재무팀": ["법인세법", "부가가치세법", "조세특례제한법", "자본시장과 금융투자업에 관한 법률", "상법"]
    }
    curr_kw = DEPT_KEYWORDS.get(dept, sum(DEPT_KEYWORDS.values(), []))
    EXCLUDE_KEYWORDS = ["공무원", "군인", "군용", "군사", "민주화운동", "직제", "소속기관", "교육감", "교원", "지방의회", "정부조직"]
    
    all_raw = []
    ninety_days_ago = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%Y%m%d')
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    for kw in curr_kw:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # 🐢 서버 과부하 방지를 위한 미세한 시간차 (0.5초)
                time.sleep(0.5) 
                
                res = session.get(BASE_URL_LAW, params={'target':'oldAndNew','type':'XML','OC':API_KEY,'query':kw}, timeout=15)
                res.raise_for_status()
                
                root = ET.fromstring(res.text)
                for item in root.findall('.//oldAndNew'):
                    name = item.findtext('신구법명', '')
                    if any(e in name for e in EXCLUDE_KEYWORDS): continue
                    if "사립학교" in name or "국가정보원" in name: continue
                    
                    p_dt, e_dt = item.findtext('공포일자',''), item.findtext('시행일자','')
                    if p_dt >= ninety_days_ago or e_dt >= ninety_days_ago:
                        dept_tag = "🗂️ 기타/공통"
                        for d_n, kws in DEPT_KEYWORDS.items():
                            if any(k in name for k in kws): dept_tag = f"📍 {d_n.replace('팀','')}/회계팀" if '재무' in d_n else f"📍 {d_n}"
                        
                        # ✨ 추가 상세 정보 가져오기 (뭐가 바뀌었는지!)
                        summary = get_law_change_summary(item.findtext('신구법일련번호',''), session)
                        
                        all_raw.append({
                            "title": name, "p_dt": p_dt, "e_dt": e_dt, "agency": item.findtext('소관부처명',''),
                            "mst_id": item.findtext('신구법일련번호',''), "dept": dept_tag,
                            "summary": summary
                        })
                break # 성공 시 리트라이 루프 탈출
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1) # 실패 시 1초 쉬고 재시도
                    continue
                st.warning(f"'{kw}' 정보를 가져오는 중 네트워크 오류 발생: {e}")
    
    unique = {l['mst_id']: l for l in all_raw}.values()
    return sorted(unique, key=lambda x: x['p_dt'], reverse=True)

# 7. 팝업 퀴즈
@st.dialog("🤖 AI 실무 퀴즈")
def quiz_modal(law):
    with st.spinner("AI가 퀴즈를 생성하고 있습니다..."):
        q = generate_quiz_from_ai({'law_name':law['title'], 'enf_dt':law['e_dt'], 'mst_id':law['mst_id']})
    
    if q:
        st.subheader(f"Q. {q['question']}")
        st.write("")
        choice = st.radio("보기에서 정답을 골라보세요:", q['options'])
        if st.button("정답 확인", type="primary", use_container_width=True):
            if choice == q['answer']: st.success("🎉 정답입니다!")
            else: st.error(f"❌ 아쉽네요. 정답은 {q['answer']} 입니다.")
            st.info(f"**💡 해설**\n{q['explanation']}")
    else: st.error("퀴즈 생성에 실패했습니다.")

# 8. 메인 컨텐츠 렌더링 (사이드바 선택에 따라 전환)
if "실시간 법령 피드" in selected_page:
    st.title("⚖️ 무한상사 Raw-bot")
    st.markdown("### 좋은 하루되세요, 경영지원본부 임직원 여러분! 🌞")
    st.markdown("<p style='color:#868e96; margin-top:-10px;'>최근 90일간 업데이트된 핵심 법령을 확인하세요.</p>", unsafe_allow_html=True)

    # 지표 섹션 (커스텀 카드)
    laws = get_laws_sync(selected_dept, limit)
    st.markdown(f"""
    <div class="summary-card-container">
        <div class="summary-card">
            <div class="summary-icon" style="background:#e7f5ff; color:#228be6;">📝</div>
            <div>
                <div class="sum-label">최근 90일 법령 개정</div>
                <div class="sum-val">{len(laws)} <span style='font-size:18px; font-weight:400;'>건</span></div>
            </div>
        </div>
        <div class="summary-card">
            <div class="summary-icon" style="background:#f3f0ff; color:#7950f2;">👥</div>
            <div>
                <div class="sum-label">부서별 태깅 완료</div>
                <div class="sum-val">100 <span style='font-size:18px; font-weight:400;'>%</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"#### 최근 업데이트 리스트({limit}개)")

    # 2개 컬럼 그리드
    display_list = laws[:limit]
    cols = st.columns(2)

    for i, law in enumerate(display_list):
        with cols[i % 2]:
            # 🎨 화면에 표시할 데이터 미리 가공
            p_dt, e_dt = law['p_dt'], law['e_dt']
            prom_dt_str = f"{p_dt[:4]}-{p_dt[4:6]}-{p_dt[6:]}" if len(p_dt) == 8 else p_dt
            enf_dt_str = f"{e_dt[:4]}-{e_dt[4:6]}-{e_dt[6:]}" if len(e_dt) == 8 else (e_dt if e_dt else "미상")
            
            summary_html = ""
            if law.get('summary'):
                summary_html = f'<div class="law-info" style="color:#228be6; font-weight:500; margin-top:5px;">{law["summary"]}</div>'

            # 🛠️ 스트림릿의 마크다운 해석 오류를 방지하기 위해 벽에 바짝 붙여서 작성! (들여쓰기 절대 금지)
            html_content = f"""<div class="law-card"><div class="law-card-content"><div class="law-badge-area"><span class="law-dept-badge">{law['dept']}</span><span class="law-new-badge">NEW</span></div><div class="law-title">{law['title']}</div><div class="law-info">공포: {prom_dt_str} | 시행: {enf_dt_str}</div><div class="law-info">주관: {law['agency']}</div>{summary_html}</div></div>"""
            st.markdown(html_content, unsafe_allow_html=True)
            
            act_col1, act_col2 = st.columns([1, 1])
            with act_col1:
                # 🔗 모든 탭이 살아있으면서, '신구법비교' 탭이 자동으로 선택되도록 파라미터 추가
                st.link_button("👉 상세 정보(신구법)", f"https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq={law['mst_id']}&viewCls=lsOldAndNew", use_container_width=True)
            with act_col2:
                if st.button("🤖 AI 퀴즈", key=f"q_{law['mst_id']}", use_container_width=True):
                    quiz_modal(law)
            st.write("") 

else: # AI 법무 챗봇 페이지
    st.markdown("### 💬 AI 법무 챗봇 '무한raw봇'")
    st.markdown("<p style='color:#868e96; margin-top:-10px;'>사내 규정 및 법률 관련 궁금한 점을 물어보세요.</p>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 경영지원본부 AI 무한raw봇입니다. 무엇을 도와드릴까요?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("질문을 입력해주세요 (예: 연차 휴가 규정 알려줘)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("규정을 분석 중입니다..."):
                results = rag_search(prompt, top_k=3)
                if results:
                    context = "\n".join([r['text'] for r in results])
                    from openai import OpenAI
                    o_client = OpenAI()
                    res = o_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "사내 규정 전문가 AI 무한raw봇입니다. 주어진 사내 규정 텍스트를 기반으로 답변하세요."},
                            {"role": "user", "content": f"[규정]\n{context}\n\n[질문]\n{prompt}"}
                        ]
                    )
                    ans = res.choices[0].message.content
                else: ans = "관련 규정을 찾을 수 없습니다."
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

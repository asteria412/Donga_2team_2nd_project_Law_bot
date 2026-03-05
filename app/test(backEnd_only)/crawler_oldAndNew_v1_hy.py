import os, json, time, requests, urllib3
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LIST_URL   = "http://www.law.go.kr/DRF/lawSearch.do"
DETAIL_URL = "http://www.law.go.kr/DRF/lawService.do"
MAIN_URL   = "https://www.law.go.kr"
OC_ID      = os.getenv("LAW_OC_ID", "test")
OUTPUT_DIR = r"C:\workAI\mini-proj-test\Donga_2team_2nd_project_Law_bot\app\test(backEnd_only)\output"
LAW_FILE   = os.path.join(OUTPUT_DIR, "law_old_new.json")

GLOBAL_SESSION = requests.Session()
GLOBAL_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://www.law.go.kr/",
    "Connection": "keep-alive",
})

def _api_get(url, params):
    try:
        resp = GLOBAL_SESSION.get(url, params=params, timeout=10, verify=False)
        print(f"🔗 요청 URL: {resp.url}")
        print(f"📡 상태코드: {resp.status_code}")
        resp.raise_for_status()
        try:
            return resp.json()
        except json.JSONDecodeError:
            print("❌ JSON 파싱 실패")
            print("응답 원문:", resp.text[:300])
            return {}
    except Exception as e:
        print(f"❌ API 오류: {e}")
        return {}

def initialize_session():
    """법제처 메인 페이지 방문으로 세션 쿠키 획득"""
    for attempt in range(4):
        try:
            GLOBAL_SESSION.get(MAIN_URL, timeout=15, verify=False)
            print("✅ 법제처 세션 초기화 완료")
            return True
        except requests.exceptions.RequestException as e:
            if attempt == 3:
                print(f"❌ 세션 초기화 최종 실패: {e}")
                return False
            wait = 2 ** attempt
            print(f"❌ 세션 초기화 실패 (재시도 {attempt+1}/3) | 대기 {wait}s: {e}")
            time.sleep(wait)

def fetch_old_and_new_list(query: str, display: int = 5, page: int = 1) -> dict:
    return _api_get(LIST_URL, {
        "OC": OC_ID,
        "target": "oldAndNew",
        "type": "JSON",
        "search": 1,
        "query": query,
        "display": display,
        "page": page,
    })

def fetch_old_and_new_detail(mst: str) -> dict:
    return _api_get(DETAIL_URL, {
        "OC": OC_ID,
        "target": "oldAndNew",
        "type": "JSON",
        "MST": mst,
    })

def collect_law(query: str) -> dict:
    print(f"\n[신구법 수집 시작] {query}")

    list_result = fetch_old_and_new_list(query=query)
    if not list_result:
        print("❌ 목록 조회 실패")
        return {}

    items = list_result.get("OldAndNewLawSearch", {}).get("oldAndNew", [])
    if isinstance(items, dict):
        items = [items]
    if not items:
        print("❌ 목록 결과 없음")
        return {}

    first = items[0]
    mst_value = first.get("신구법일련번호")
    law_name = first.get("신구법명", query)
    print(f"✅ MST 추출 완료 | 법령명: {law_name} | MST: {mst_value}")

    detail_result = fetch_old_and_new_detail(mst=mst_value)
    if not detail_result:
        print("❌ 본문 조회 실패")
        return {}

    result = {"법령명": law_name, "MST": mst_value, "목록결과": list_result, "본문결과": detail_result}

    # 기존 파일 읽어서 중복 제거 후 저장
    if os.path.exists(LAW_FILE):
        with open(LAW_FILE, "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
            except json.JSONDecodeError:
                old_data = []
    else:
        old_data = []

    seen = {item.get("MST") for item in old_data}
    if mst_value not in seen:
        old_data.append(result)

    with open(LAW_FILE, "w", encoding="utf-8") as f:
        json.dump(old_data, f, ensure_ascii=False, indent=2)
    print(f"💾 저장 완료: {LAW_FILE} | 총 {len(old_data)}건")

    return result

def update_laws():
    for query in [
    "근로기준법",
    "산업안전보건법",
    "남녀고용평등법",
    "상법",
    "법인세법",
    "조세특례제한법",
    "자본시장과 금융투자업에 관한 법률",
    "부가가치세법",
    "공정거래법",
    "개인정보보호법"]:
        collect_law(query)

def initial_check():
    """law_old_new.json이 없거나 비어있으면 즉시 데이터 수집"""
    if not os.path.exists(LAW_FILE):
        print("⚠️ 파일 없음 → 즉시 데이터 수집")
        update_laws()
    else:
        with open(LAW_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
        if not data:
            print("⚠️ 파일 비어있음 → 즉시 데이터 수집")
            update_laws()
        else:
            print("✅ 기존 데이터 존재")
            
'''#테스트 위해 업데이트 예약 비활성화
def schedule_job():
    seoul_tz = pytz.timezone("Asia/Seoul")
    scheduler = BackgroundScheduler(timezone=seoul_tz)
    scheduler.add_job(update_laws, "cron", hour=21, minute=0, second=0)
    scheduler.start()
    print("⏰ 매일 21:00 서울시간에 신구법 업데이트 예약 완료")

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
'''
if __name__ == "__main__":
    initialize_session()
    initial_check()
    #schedule_job() #테스트 위해 업데이트 예약 비활성화

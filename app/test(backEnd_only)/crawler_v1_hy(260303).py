# app/collector/crawler.py

# --- [필수 라이브러리 임포트] ---
import os
import json
import urllib3
import requests
from dotenv import load_dotenv

# --- [환경 변수 로드] ---
load_dotenv()

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- [전역 상수 선언] ---
# 가이드 원문 URL 기준으로 확정
LIST_URL    = "http://www.law.go.kr/DRF/lawSearch.do"    # 목록 조회: lawSearch.do
DETAIL_URL  = "http://www.law.go.kr/DRF/lawService.do"   # 본문 조회: lawService.do
MAIN_URL    = "https://www.law.go.kr"                     # 세션 쿠키 획득용
OC_ID       = os.getenv("LAW_OC_ID", "test")             # .env 우선, 없으면 test
OUTPUT_TYPE = "JSON"                                       # 출력 형태 고정

# 수집 대상 법령 목록 — 추가 시 리스트에 append
TARGET_LAWS = [
    "부가가치세법"
]

# --- [전역 Session 선언] ---
GLOBAL_SESSION = requests.Session()
GLOBAL_SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept"         : "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer"        : "https://www.law.go.kr/",
    "Connection"     : "keep-alive",
})


# ────────────────────────────────────────────────────────────
# 세션 초기화 — 메인 페이지 방문으로 쿠키 획득 (1회 실행)
# ────────────────────────────────────────────────────────────
def initialize_session() -> bool:
    """
    법제처 메인 페이지를 방문하여 세션 쿠키를 획득
    서버 시작 시 1회 실행

    Returns:
        bool : 세션 초기화 성공 여부
    """
    try:
        GLOBAL_SESSION.get(MAIN_URL, timeout=20, verify=False)
        print("✅ 법제처 세션 초기화 완료")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 세션 초기화 실패: {e}")
        return False


# ────────────────────────────────────────────────────────────
# 함수 1 : 신구법 목록 조회
# 가이드 원문 URL : http://www.law.go.kr/DRF/lawSearch.do
# 가이드 원문 target : oldAndNew
# ────────────────────────────────────────────────────────────
def fetch_old_and_new_list(
    query: str,
    search: int = 1,
    display: int = 5,
    page: int = 1,
) -> dict:
    """
    법제처 API - 신구법 목록 조회

    요청 URL : http://www.law.go.kr/DRF/lawSearch.do?target=oldAndNew

    Args:
        query   : 검색어 (법령명 또는 법령ID)
        search  : 검색 구분 (1=법령명 / 2=법령ID)
        display : 검색 결과 수 (기본 5)
        page    : 페이지 번호 (기본 1)

    Returns:
        dict : API 응답 JSON
    """
    params = {
        "OC"     : OC_ID,       # 필수: 이메일 ID
        "target" : "oldAndNew", # 필수: 가이드 원문 고정값
        "type"   : OUTPUT_TYPE, # 필수: JSON
        "search" : search,      # 필수: 검색 구분
        "query"  : query,       # 검색어
        "display": display,     # 결과 수
        "page"   : page,        # 페이지
    }

    try:
        response = GLOBAL_SESSION.get(
            LIST_URL,           # lawSearch.do
            params=params,
            timeout=10,
            verify=False
        )
        print(f"  🔗 요청 URL : {response.url}")
        print(f"  📡 상태코드 : {response.status_code}")
        response.raise_for_status()

        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"  ❌ JSON 파싱 실패 | 응답 원문: {response.text[:300]}")
            return {}

    except requests.exceptions.Timeout:
        print("  ❌ 오류: API 요청 시간 초과")
        return {}
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ HTTP 오류: {e}")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 네트워크 오류: {e}")
        return {}


# ────────────────────────────────────────────────────────────
# 함수 2 : 신구법 본문 조회
# 가이드 원문 URL : http://www.law.go.kr/DRF/lawService.do
# 가이드 원문 target : oldAndNew
# ────────────────────────────────────────────────────────────
def fetch_old_and_new_detail(
    law_id: str = None,
    mst: str = None,
    lm: str = None,
    ld: int = None,
    ln: int = None,
) -> dict:
    """
    법제처 API - 신구법 본문 조회

    요청 URL : http://www.law.go.kr/DRF/lawService.do?target=oldAndNew

    Args:
        law_id : 법령 ID → 파라미터 키 'ID' (ID 또는 mst 중 하나 필수)
        mst    : 법령 마스터 번호 → 파라미터 키 'MST' (lsi_seq 값)
        lm     : 법령명 → 파라미터 키 'LM' (선택)
        ld     : 공포일자 → 파라미터 키 'LD' (선택)
        ln     : 공포번호 → 파라미터 키 'LN' (선택)

    Returns:
        dict : API 응답 JSON
              신구법존재여부 == 'N' 이면 신구법 데이터 없음
    """
    if not law_id and not mst:
        print("  ❌ 오류: law_id(ID) 또는 mst(MST) 중 하나는 반드시 입력해야 합니다.")
        return {}

    params = {
        "OC"    : OC_ID,       # 필수: 이메일 ID
        "target": "oldAndNew", # 필수: 가이드 원문 고정값
        "type"  : OUTPUT_TYPE, # 필수: JSON
    }

    # None 값은 파라미터에서 제외
    if law_id : params["ID"]  = law_id
    if mst    : params["MST"] = mst
    if lm     : params["LM"]  = lm
    if ld     : params["LD"]  = ld
    if ln     : params["LN"]  = ln

    try:
        response = GLOBAL_SESSION.get(
            DETAIL_URL,         # lawService.do
            params=params,
            timeout=10,
            verify=False
        )
        print(f"  🔗 요청 URL : {response.url}")
        print(f"  📡 상태코드 : {response.status_code}")
        response.raise_for_status()

        try:
            result = response.json()
        except json.JSONDecodeError:
            print(f"  ❌ JSON 파싱 실패 | 응답 원문: {response.text[:300]}")
            return {}

        # 가이드 원문: 신구법존재여부 == 'N' 이면 데이터 없음
        existence = (
            result
            .get("신구법본문조회", {})
            .get("신구법존재여부", "Y")
        )
        if existence == "N":
            print("  ⚠️ 안내: 해당 법령의 신구법 데이터가 존재하지 않습니다.")

        return result

    except requests.exceptions.Timeout:
        print("  ❌ 오류: API 요청 시간 초과")
        return {}
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ HTTP 오류: {e}")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 네트워크 오류: {e}")
        return {}


# ────────────────────────────────────────────────────────────
# 함수 3 : 단일 법령 수집 (목록 → MST 추출 → 본문)
# ────────────────────────────────────────────────────────────
def collect_law(query: str) -> dict:
    """
    단일 법령에 대해 목록 조회 → MST 추출 → 본문 조회 순서 실행

    Args:
        query : 수집할 법령명

    Returns:
        dict : {
            "법령명"   : str,
            "MST"     : str,
            "목록결과" : dict,
            "본문결과" : dict,
        }
    """
    print(f"\n{'─' * 60}")
    print(f"[수집 시작] {query}")
    print(f"{'─' * 60}")

    # ── PHASE 1 : 목록 조회 ─────────────────────────────────
    print("\n[PHASE 1] 신구법 목록 조회")
    list_result = fetch_old_and_new_list(
        query=query, search=1, display=5, page=1
    )

    if not list_result:
        print(f"  ❌ '{query}' 목록 조회 실패")
        return {}

    print(f"\n  📋 목록 조회 결과:")
    print(json.dumps(list_result, ensure_ascii=False, indent=2))

    # ── MST 추출 ────────────────────────────────────────────
    try:
        law_items = (
            list_result
            .get("OldAndNewLawSearch", {})
            .get("oldAndNew", [])
        )

        # 단건(dict) / 다건(list) 응답 통일 처리
        if isinstance(law_items, dict):
            law_items = [law_items]

        if not law_items:
            print(f"  ⚠️ '{query}' 검색 결과 없음")
            return {}

        first_law = law_items[0]
        mst_value = first_law.get("신구법일련번호", None)
        law_name  = first_law.get("신구법명", query)

        if not mst_value:
            print(f"  ❌ MST 추출 실패 | 응답 키 확인 필요")
            return {}

        print(f"\n  ✅ MST 추출 완료 | 법령명: {law_name} | MST: {mst_value}")

    except (KeyError, IndexError, TypeError) as e:
        print(f"  ❌ MST 추출 오류: {e}")
        return {}

    # ── PHASE 2 : 본문 조회 ─────────────────────────────────
    print(f"\n[PHASE 2] 신구법 본문 조회 | MST: {mst_value}")
    detail_result = fetch_old_and_new_detail(mst=mst_value)

    if not detail_result:
        print(f"  ❌ '{query}' 본문 조회 실패")
        return {}

    print(f"\n  📄 본문 조회 결과:")
    print(json.dumps(detail_result, ensure_ascii=False, indent=2))

    return {
        "법령명"  : law_name,
        "MST"    : mst_value,
        "목록결과": list_result,
        "본문결과": detail_result,
    }


# ────────────────────────────────────────────────────────────
# 함수 4 : 수집 진입점 — TARGET_LAWS 전체 순회
# ────────────────────────────────────────────────────────────
def run_collector(law_list: list = None) -> list:
    """
    TARGET_LAWS 또는 전달받은 법령 목록 전체를 순서대로 수집

    Args:
        law_list : 수집할 법령명 리스트
                   None 이면 전역 TARGET_LAWS 사용

    Returns:
        list : 수집된 법령 데이터 목록
    """
    targets   = law_list if law_list else TARGET_LAWS
    collected = []

    print("\n" + "=" * 60)
    print(f"[전체 수집 시작] 총 {len(targets)}개 법령")
    print(f"대상: {', '.join(targets)}")
    print("=" * 60)

    for idx, law_name in enumerate(targets, start=1):
        print(f"\n[{idx}/{len(targets)}] {law_name} 수집 중...")
        result = collect_law(query=law_name)

        if result:
            collected.append(result)
            print(f"\n  ✅ [{idx}/{len(targets)}] '{law_name}' 수집 완료")
        else:
            print(f"\n  ⚠️ [{idx}/{len(targets)}] '{law_name}' 수집 실패 — 건너뜁니다")

    print("\n" + "=" * 60)
    print(f"✅ 전체 수집 완료 | 성공: {len(collected)}/{len(targets)}건")
    print("=" * 60)

    return collected


# ────────────────────────────────────────────────────────────
# __main__ : 직접 실행 시 자동 구동
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    initialize_session()  # 세션 초기화 (쿠키 획득) 1회
    run_collector()       # TARGET_LAWS 전체 수집


'''
(.venv) C:\workAI\mini-proj-test\Donga_2team_2nd_project_Law_bot>c:\workAI\mini-proj-test\Donga_2team_2nd_project_Law_bot\.venv\Scripts\python.exe "c:/workAI/mini-proj-test/Donga_2team_2nd_project_Law_bot/app/test(backEnd_only)/crawler.py"
❌ 세션 초기화 실패: HTTPSConnectionPool(host='www.law.go.kr', port=443): Read timed out. (read timeout=10)

============================================================
[전체 수집 시작] 총 1개 법령
대상: 부가가치세법
============================================================

[1/1] 부가가치세법 수집 중...

────────────────────────────────────────────────────────────
[수집 시작] 부가가치세법
────────────────────────────────────────────────────────────

[PHASE 1] 신구법 목록 조회
  🔗 요청 URL : http://www.law.go.kr/DRF/lawSearch.do?OC=00blueangel&target=oldAndNew&type=JSON&search=1&query=%EB%B6%80%EA%B0%80%EA%B0%80%EC%B9%98%EC%84%B8%EB%B2%95&display=5&page=1
  📡 상태코드 : 200

  📋 목록 조회 결과:
{
  "OldAndNewLawSearch": {
    "resultMsg": "success",
    "키워드": "부가가치세법",
    "page": "1",
    "resultCode": "00",
    "target": "oldAndNew",
    "oldAndNew": [
      {
        "현행연혁코드": "현행",
        "id": "1",
        "신구법ID": "001571",
        "신구법상세링크": "/DRF/lawService.do?OC=00blueangel&target=oldAndNew&MST=276117&type=HTML&mobileYn=",
        "시행일자": "20260102",
        "법령구분명": "법률",
        "소관부처명": "재정경제부",
        "공포번호": "21065",
        "신구법일련번호": "276117",
        "제개정구분명": "타법개정",
        "공포일자": "20251001",
        "소관부처코드": "1053000",
        "신구법명": "부가가치세법"
      },
      {
        "현행연혁코드": "현행",
        "id": "2",
        "신구법ID": "003666",
        "신구법상세링크": "/DRF/lawService.do?OC=00blueangel&target=oldAndNew&MST=283641&type=HTML&mobileYn=",
        "시행일자": "20260227",
        "법령구분명": "대통령령",
        "소관부처명": "재정경제부,재정경제부",
        "공포번호": "36133",
        "신구법일련번호": "283641",
        "제개정구분명": "일부개정",
        "공포일자": "20260227",
        "소관부처코드": "1053000 1053000",
        "신구법명": "부가가치세법 시행령"
      },
      {
        "현행연혁코드": "현행",
        "id": "3",
        "신구법ID": "007289",
        "신구법상세링크": "/DRF/lawService.do?OC=00blueangel&target=oldAndNew&MST=282645&type=HTML&mobileYn=",
        "시행일자": "20260102",
        "법령구분명": "재정경제부령",
        "소관부처명": "재정경제부",
        "공포번호": "00001",
        "신구법일련번호": "282645",
        "제개정구분명": "타법개정",
        "공포일자": "20260102",
        "소관부처코드": "1053000",
        "신구법명": "부가가치세법 시행규칙"
      }
    ],
    "totalCnt": "3",
    "section": "lawNm",
    "numOfRows": "3"
  }
}

  ✅ MST 추출 완료 | 법령명: 부가가치세법 | MST: 276117

[PHASE 2] 신구법 본문 조회 | MST: 276117
  🔗 요청 URL : http://www.law.go.kr/DRF/lawService.do?OC=00blueangel&target=oldAndNew&type=JSON&MST=276117
  📡 상태코드 : 200

  📄 본문 조회 결과:
{
  "OldAndNewService": {
    "신조문목록": {
      "조문": [
        {
          "content": "제21조(재화의 수출) ① (현행과 같음)",
          "no": "1"
        },
        {
          "content": "② 제1항에 따른 수출은 다음 각 호의 것으로 한다.",
          "no": "2"
        },
        {
          "content": "1.·2. (현행과 같음)",
          "no": "3"
        },
        {
          "content": "3. <P>재정경제부령</P>으로 정하는 내국신용장 또는 구매확인서에 의하여 재화[금지금(金地金)은 제외한다]를 공급하는 것 등으로서 대통령령으로 정하는 것",
          "no": "4"
        },
        {
          "content": "제47조(전자세금계산서 발급 전송에 대한 세액공제 특례) ①·② (현행과 같음)",
          "no": "5"
        },
        {
          "content": "③ 제1항에 따른 세액공제를 적용받으려는 개인사업자는 제48조 및 제49조에 따라 신고할 때 <P>재정경제부령</P>으로 정하는 전자세금계산서 발급세액공제신고서를 납세지 관할 세무서장에게 제출하여야 한다.",  
          "no": "6"
        },
        {
          "content": "제53조의2(전자적 용역을 공급하는 국외사업자의 사업자등록 및 납부 등에 관한 특례) ① ∼ ⑥ (현행과 같음)",
          "no": "7"
        },
        {
          "content": "⑦ 국세청장은 부가가치세 신고의 적정성을 확인하기 위하여 간편사업자등록을 한 자에게 <P>재정경제부령</P>으로 정하는 전자적 용역 거래명세서(이하 이 조에서 “전자적 용역 거래명세서”라 한다)를 제출할 것을 요구할 수 있다.",
          "no": "8"
        },
        {
          "content": "⑧ ∼ ⑩ (현행과 같음)",
          "no": "9"
        },
        {
          "content": "제55조(현금매출명세서 등의 제출) ① 다음 각 호의 사업 중 해당 업종의 특성 및 세원관리(稅 源管理)를 고려하여 대통령령으로 정하는 사업을 하는 사업자는 예정신고 또는 확정신고를 할 때 <P>재정경제부령</P>으로 정하는 현금매출명세서를 함께 제출하여야 한다.",
          "no": "10"
        },
        {
          "content": "1. ∼ 4. (현행과 같음)",
          "no": "11"
        },
        {
          "content": "② 부동산임대업자는 <P>재정경제부령</P>으로 정하는 부동산임대공급가액명세서를 예정신고 또는 확정신고를 할 때 함께 제출하여야 한다.",
          "no": "12"
        },
        {
          "content": "③ (현행과 같음)",
          "no": "13"
        },
        {
          "content": "제63조(간이과세자의 과세표준과 세액) ① ∼ ③ (현행과 같음)",
          "no": "14"
        },
        {
          "content": "④ 간이과세자(제36조제1항제2호 각 목의 어느 하나에 해당하는 간이과세자는 제외한다)가 전자세금계산서를 2027년 12월 31일까지 발급(전자세금계산서 발급명세를 제32조제3항에 따른 기한까지 국세청장에게 전송한 경우로 한정한다)하고 <P>재정경제부령</P>으로 정하는 전자세금계산서 발급세액공제신고서를 납세지 관할 세무서 장에게 제출한 경우의 해당 과세기간에 대한 부가가치세액 공제에 관하여는 제47조제1항을 준용한다.",
          "no": "15"
        },
        {
          "content": "⑤ ∼ ⑦ (현행과 같음)",
          "no": "16"
        }
      ]
    },
    "구조문목록": {
      "조문": [
        {
          "content": "제21조(재화의 수출) ① (생  략)",
          "no": "1"
        },
        {
          "content": "② 제1항에 따른 수출은 다음 각 호의 것으로 한다.",
          "no": "2"
        },
        {
          "content": "1.·2. (생  략)",
          "no": "3"
        },
        {
          "content": "3. <P>기획재정부령</P>으로 정하는 내국신용장 또는 구매확인서에 의하여 재화[금지금(金地金)은 제외한다]를 공급하는 것 등으로서 대통령령으로 정하는 것",
          "no": "4"
        },
        {
          "content": "제47조(전자세금계산서 발급 전송에 대한 세액공제 특례) ①·② (생  략)",
          "no": "5"
        },
        {
          "content": "③ 제1항에 따른 세액공제를 적용받으려는 개인사업자는 제48조 및 제49조에 따라 신고할 때 <P>기획재정부령</P>으로 정하는 전자세금계산서 발급세액공제신고서를 납세지 관할 세무서장에게 제출하여야 한다.",  
          "no": "6"
        },
        {
          "content": "제53조의2(전자적 용역을 공급하는 국외사업자의 사업자등록 및 납부 등에 관한 특례) ① ∼ ⑥ (생  략)",
          "no": "7"
        },
        {
          "content": "⑦ 국세청장은 부가가치세 신고의 적정성을 확인하기 위하여 간편사업자등록을 한 자에게 <P>기획재정부령</P>으로 정하는 전자적 용역 거래명세서(이하 이 조에서 “전자적 용역 거래명세서”라 한다)를 제출할 것을 요구할 수 있다.",
          "no": "8"
        },
        {
          "content": "⑧ ∼ ⑩ (생  략)",
          "no": "9"
        },
        {
          "content": "제55조(현금매출명세서 등의 제출) ① 다음 각 호의 사업 중 해당 업종의 특성 및 세원관리(稅 源管理)를 고려하여 대통령령으로 정하는 사업을 하는 사업자는 예정신고 또는 확정신고를 할 때 <P>기획재정부령</P>으로 정하는 현금매출명세서를 함께 제출하여야 한다.",
          "no": "10"
        },
        {
          "content": "1. ∼ 4. (생  략)",
          "no": "11"
        },
        {
          "content": "② 부동산임대업자는 <P>기획재정부령</P>으로 정하는 부동산임대공급가액명세서를 예정신고 또는 확정신고를 할 때 함께 제출하여야 한다.",
          "no": "12"
        },
        {
          "content": "③ (생  략)",
          "no": "13"
        },
        {
          "content": "제63조(간이과세자의 과세표준과 세액) ① ∼ ③ (생  략)",
          "no": "14"
        },
        {
          "content": "④ 간이과세자(제36조제1항제2호 각 목의 어느 하나에 해당하는 간이과세자는 제외한다)가 전자세금계산서를 2027년 12월 31일까지 발급(전자세금계산서 발급명세를 제32조제3항에 따른 기한까지 국세청장에게 전송한 경우로 한정한다)하고 <P>기획재정부령</P>으로 정하는 전자세금계산서 발급세액공제신고서를 납세지 관할 세무서 장에게 제출한 경우의 해당 과세기간에 대한 부가가치세액 공제에 관하여는 제47조제1항을 준용한다.",
          "no": "15"
        },
        {
          "content": "⑤ ∼ ⑦ (생  략)",
          "no": "16"
        }
      ]
    },
    "구조문_기본정보": {
      "현행여부": "N",
      "법령ID": "001571",
      "법령일련번호": "269797",
      "법종구분": "법률",
      "법령명": "부가가치세법",
      "시행일자": "20250701",
      "공포번호": "20776",
      "제개정구분명": "일부개정",
      "공포일자": "20250314"
    },
    "신조문_기본정보": {
      "현행여부": "Y",
      "법령ID": "001571",
      "법령일련번호": "276117",
      "법종구분": "법률",
      "법령명": "부가가치세법",
      "시행일자": "20260102",
      "공포번호": "21065",
      "제개정구분명": "타법개정",
      "공포일자": "20251001"
    }
  }
}

  ✅ [1/1] '부가가치세법' 수집 완료

============================================================
✅ 전체 수집 완료 | 성공: 1/1건
============================================================'''
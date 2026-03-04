# app/collector/crawler.py

import os
import json
import time
import urllib3
import requests
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── 전역 상수 ────────────────────────────────────────────────
LIST_URL    = "http://www.law.go.kr/DRF/lawSearch.do"
DETAIL_URL  = "http://www.law.go.kr/DRF/lawService.do"
MAIN_URL    = "https://www.law.go.kr"
OC_ID       = os.getenv("LAW_OC_ID", "test")
OUTPUT_TYPE = "JSON"

TARGET_LAWS         = ["근로기준법"]
TARGET_PREC_QUERIES = ["근로기준법"]

OUTPUT_DIR_ABS       = r"C:\workAI\mini-proj-test\Donga_2team_2nd_project_Law_bot\app\test(backEnd_only)\output"
OUTPUT_DIR           = OUTPUT_DIR_ABS
DEFAULT_OUTPUT_FILE  = "law_old_new.json"
DEFAULT_PREC_OUTPUT_FILE = "law_prec.json"

print(f"[DEBUG] OUTPUT_DIR: {OUTPUT_DIR} (존재: {os.path.isdir(OUTPUT_DIR)})")

# ── 전역 Session ─────────────────────────────────────────────
GLOBAL_SESSION = requests.Session()
GLOBAL_SESSION.headers.update({
    "User-Agent"     : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept"         : "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer"        : "https://www.law.go.kr/",
    "Connection"     : "keep-alive",
})


# ════════════════════════════════════════════════════════════
# 공통 유틸
# ════════════════════════════════════════════════════════════

def save_json_to_file(data: dict, filepath: str) -> None:
    """JSON 파일 저장 (덮어쓰기, ensure_ascii=False)"""
    dirpath = os.path.dirname(filepath)
    if not os.path.isdir(dirpath):
        print(f"❌ 저장 실패: 디렉터리 미존재 - {dirpath}")
        return
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 저장 완료: {filepath}")
    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")


def _normalize_list(items) -> list:
    """단건(dict) / 다건(list) 응답을 list로 통일"""
    if isinstance(items, dict):
        return [items]
    return items if isinstance(items, list) else []


def _api_get(url: str, params: dict) -> dict:
    """
    공통 HTTP GET 요청 래퍼.
    성공 시 dict 반환, 실패 시 {} 반환.
    """
    try:
        resp = GLOBAL_SESSION.get(url, params=params, timeout=10, verify=False)
        print(f"  🔗 요청 URL : {resp.url}")
        print(f"  📡 상태코드 : {resp.status_code}")
        resp.raise_for_status()
        try:
            return resp.json()
        except json.JSONDecodeError:
            print(f"  ❌ JSON 파싱 실패 | 응답 원문: {resp.text[:300]}")
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


def _run_collector_loop(
    targets: list,
    collect_fn,          # collect_law | collect_prec
    label: str,
    delay: float = 1.0,
) -> list:
    """
    공통 수집 루프.
    targets 를 순회하며 collect_fn 호출 → 결과 누적 → 딜레이 적용.
    """
    collected = []
    print("\n" + "=" * 60)
    print(f"[{label} 전체 수집 시작] 총 {len(targets)}개")
    print(f"대상: {', '.join(targets)}")
    print("=" * 60)

    for idx, target in enumerate(targets, start=1):
        print(f"\n[{idx}/{len(targets)}] '{target}' 수집 중...")
        result = collect_fn(target)
        if result:
            collected.append(result)
            print(f"  ✅ [{idx}/{len(targets)}] '{target}' 수집 완료")
        else:
            print(f"  ⚠️ [{idx}/{len(targets)}] '{target}' 수집 실패 — 건너뜁니다")
        if idx < len(targets):          # 마지막 항목엔 딜레이 불필요
            time.sleep(delay)

    print("\n" + "=" * 60)
    print(f"✅ {label} 전체 수집 완료 | 성공: {len(collected)}/{len(targets)}건")
    print("=" * 60)
    return collected


# ════════════════════════════════════════════════════════════
# 세션 초기화
# ════════════════════════════════════════════════════════════

def initialize_session() -> bool:
    """법제처 메인 페이지 방문으로 세션 쿠키 획득 (서버 시작 시 1회)"""
    for attempt in range(4):            # 0~3 → 최대 4회 시도
        try:
            GLOBAL_SESSION.get(MAIN_URL, timeout=15, verify=False)
            print("✅ 법제처 세션 초기화 완료")
            return True
        except requests.exceptions.RequestException as e:
            if attempt == 3:
                print(f"❌ 세션 초기화 최종 실패: {e}")
                return False
            wait = 2 ** attempt         # 1 → 2 → 4초
            print(f"❌ 세션 초기화 실패 (재시도 {attempt + 1}/3) | 대기 {wait}s: {e}")
            time.sleep(wait)


# ════════════════════════════════════════════════════════════
# 신구법 API
# ════════════════════════════════════════════════════════════

def fetch_old_and_new_list(
    query: str,
    search: int = 1,
    display: int = 5,
    page: int = 1,
) -> dict:
    """법제처 API - 신구법 목록 조회 (lawSearch.do?target=oldAndNew)"""
    return _api_get(LIST_URL, {
        "OC"     : OC_ID,
        "target" : "oldAndNew",
        "type"   : OUTPUT_TYPE,
        "search" : search,
        "query"  : query,
        "display": display,
        "page"   : page,
    })


def fetch_old_and_new_detail(
    law_id: str = None,
    mst: str = None,
    lm: str = None,
    ld: int = None,
    ln: int = None,
) -> dict:
    """법제처 API - 신구법 본문 조회 (lawService.do?target=oldAndNew)"""
    if not law_id and not mst:
        print("  ❌ 오류: law_id(ID) 또는 mst(MST) 중 하나는 필수입니다.")
        return {}

    params = {"OC": OC_ID, "target": "oldAndNew", "type": OUTPUT_TYPE}
    # None 값 제외
    for key, val in [("ID", law_id), ("MST", mst), ("LM", lm), ("LD", ld), ("LN", ln)]:
        if val is not None:
            params[key] = val

    result = _api_get(DETAIL_URL, params)

    existence = result.get("신구법본문조회", {}).get("신구법존재여부", "Y")
    if existence == "N":
        print("  ⚠️ 안내: 해당 법령의 신구법 데이터가 존재하지 않습니다.")

    return result


def collect_law(query: str) -> dict:
    """신구법 단일 법령 수집: 목록 조회 → MST 추출 → 본문 조회"""
    print(f"\n{'─' * 60}\n[신구법 수집 시작] {query}\n{'─' * 60}")

    print("\n[PHASE 1] 신구법 목록 조회")
    list_result = fetch_old_and_new_list(query=query)
    if not list_result:
        print(f"  ❌ '{query}' 목록 조회 실패")
        return {}
    print(f"\n  📋 목록 결과:\n{json.dumps(list_result, ensure_ascii=False, indent=2)}")

    try:
        items     = _normalize_list(list_result.get("OldAndNewLawSearch", {}).get("oldAndNew", []))
        first     = items[0]
        mst_value = first.get("신구법일련번호")
        law_name  = first.get("신구법명", query)
    except (IndexError, TypeError) as e:
        print(f"  ❌ MST 추출 오류: {e}")
        return {}

    if not mst_value:
        print("  ❌ MST 추출 실패 | 응답 키 확인 필요")
        return {}
    print(f"  ✅ MST 추출 완료 | 법령명: {law_name} | MST: {mst_value}")

    print(f"\n[PHASE 2] 신구법 본문 조회 | MST: {mst_value}")
    detail_result = fetch_old_and_new_detail(mst=mst_value)
    if not detail_result:
        print(f"  ❌ '{query}' 본문 조회 실패")
        return {}
    print(f"\n  📄 본문 결과:\n{json.dumps(detail_result, ensure_ascii=False, indent=2)}")

    result = {"법령명": law_name, "MST": mst_value, "목록결과": list_result, "본문결과": detail_result}
    save_json_to_file(result, os.path.join(OUTPUT_DIR, DEFAULT_OUTPUT_FILE))
    return result


def run_collector(law_list: list = None) -> list:
    """신구법 수집 진입점 — TARGET_LAWS 또는 전달받은 목록 전체 수집"""
    return _run_collector_loop(
        targets    = law_list or TARGET_LAWS,
        collect_fn = collect_law,
        label      = "신구법",
    )


# ════════════════════════════════════════════════════════════
# 판례 API
# ════════════════════════════════════════════════════════════

def fetch_prec_list(
    query: str,
    search: int = 1,
    display: int = 5,
    page: int = 1,
    dat_src_nm: str = None,
) -> dict:
    """법제처 API - 판례 목록 조회 (lawSearch.do?target=prec)"""
    params = {
        "OC"     : OC_ID,
        "target" : "prec",
        "type"   : OUTPUT_TYPE,
        "search" : search,
        "query"  : query,
        "display": display,
        "page"   : page,
    }
    if dat_src_nm:
        params["datSrcNm"] = dat_src_nm
    return _api_get(LIST_URL, params)


def fetch_prec_detail(prec_id: str) -> dict:
    """법제처 API - 판례 본문 조회 (lawService.do?target=prec)"""
    if not prec_id:
        print("  ❌ 오류: prec_id(ID) 는 필수입니다.")
        return {}
    return _api_get(DETAIL_URL, {
        "OC"    : OC_ID,
        "target": "prec",
        "ID"    : prec_id,
        "type"  : OUTPUT_TYPE,
    })


def collect_prec(query: str) -> dict:
    """판례 단일 키워드 수집: 목록 조회 → ID 추출 → 본문 조회"""
    print(f"\n{'─' * 60}\n[판례 수집 시작] {query}\n{'─' * 60}")

    print("\n[PHASE 1] 판례 목록 조회")
    list_result = fetch_prec_list(query=query)
    if not list_result:
        print(f"  ❌ '{query}' 판례 목록 조회 실패")
        return {}
    print(f"\n  📋 목록 결과:\n{json.dumps(list_result, ensure_ascii=False, indent=2)}")

    try:
        items = _normalize_list(list_result.get("PrecSearch", {}).get("prec", []))
        first = items[0]
        prec_id = first.get("판례일련번호")
        prec_name = first.get("판례명", query)

        # 필요한 필드만 추출 (목록 조회)
        filtered_list = [
            {
                "사건명": item.get("사건명"),
                "사건번호": item.get("사건번호"),
                "법원명": item.get("법원명"),
                "선고일자": item.get("선고일자"),
                "판례일련번호": item.get("판례일련번호"),
            }
            for item in items
        ]
    except (IndexError, TypeError) as e:
        print(f"  ❌ 판례 ID 추출 오류: {e}")
        return {}

    if not prec_id:
        print("  ❌ 판례 ID 추출 실패 | 위 JSON 결과에서 키 이름을 확인하세요.")
        return {}
    print(f"  ✅ 판례 ID 추출 완료 | 판례명: {prec_name} | ID: {prec_id}")

    print(f"\n[PHASE 2] 판례 본문 조회 | ID: {prec_id}")
    detail_result = fetch_prec_detail(prec_id=prec_id)
    if not detail_result:
        print(f"  ❌ '{query}' 판례 본문 조회 실패")
        return {}
    print(f"\n  📄 본문 결과:\n{json.dumps(detail_result, ensure_ascii=False, indent=2)}")

    # 본문 조회에서 판결요지만 추출
    try:
        judgment_summary = detail_result.get("PrecService", {}).get("판결요지")
    except Exception:
        judgment_summary = None

    # 최종 결과: 목록(필터링된 필드만) + 본문(판결요지만)
    result = {
        "키워드": query,
        "판례ID": prec_id,
        "판례명": prec_name,
        "목록결과": filtered_list,
        "본문결과": {"판결요지": judgment_summary},
    }
    save_json_to_file(result, os.path.join(OUTPUT_DIR, DEFAULT_PREC_OUTPUT_FILE))
    return result



def run_prec_collector(query_list: list = None) -> list:
    """판례 수집 진입점 — TARGET_PREC_QUERIES 또는 전달받은 목록 전체 수집"""
    return _run_collector_loop(
        targets    = query_list or TARGET_PREC_QUERIES,
        collect_fn = collect_prec,
        label      = "판례",
    )


# ════════════════════════════════════════════════════════════
# 직접 실행 진입점
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    initialize_session()
    run_collector()
    run_prec_collector()

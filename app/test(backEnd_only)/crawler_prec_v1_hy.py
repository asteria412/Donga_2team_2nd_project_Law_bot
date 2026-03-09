import os
import re
import json
import html
import requests
from datetime import datetime
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
SERVICE_URL = "https://www.law.go.kr/DRF/lawService.do"
SAVE_PATH = r"C:\workAI\mini-proj-test\Donga_2team_2nd_project_Law_bot\data\law_data\latest_raw_collection.json"

FIELD_WEIGHTS = {
    "사건명": 0.5,
    "판시사항": 0.3,
    "판결요지": 0.2
}


def build_session():
    s = requests.Session()
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=0.7,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=1, pool_maxsize=1)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/html,*/*",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        "Connection": "close"
    })
    s.trust_env = True
    return s


def clean_text(x):
    if x is None:
        return ""
    t = html.unescape(str(x))
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def to_items(data):
    if not isinstance(data, dict):
        return []
    x = data.get("PrecSearch", {}).get("prec", [])
    if isinstance(x, dict):
        return [x]
    if isinstance(x, list):
        return x
    return []


def map_row(it):
    return {
        "사건명": it.get("사건명", "") or "",
        "사건번호": it.get("사건번호", "") or "",
        "법원명": it.get("법원명", "") or "",
        "선고일자": str(it.get("선고일자", "") or ""),
        "판례일련번호": str(it.get("판례일련번호", "") or ""),
        "판결요지": it.get("판결요지", "") or "",
        "판시사항": it.get("판시사항", "") or ""
    }


def token_overlap_score(query, text):
    q_tokens = re.findall(r"[0-9a-zA-Z가-힣]+", clean_text(query))
    if not q_tokens:
        return 0.0
    tset = set(re.findall(r"[0-9a-zA-Z가-힣]+", clean_text(text)))
    hit = sum(1 for tok in q_tokens if tok in tset)
    return hit / len(q_tokens)


def weighted_score(query, row):
    s = 0.0
    for field, w in FIELD_WEIGHTS.items():
        s += w * token_overlap_score(query, row.get(field, ""))
    return s


def extract_section_text(text, key):
    keys = ["판시사항", "판결요지", "참조조문", "참조판례", "판례내용", "주문", "이유"]
    idx = text.find(key)
    if idx < 0:
        return ""
    tail = text[idx + len(key):]
    end = len(tail)
    for k in keys:
        if k == key:
            continue
        p = tail.find(k)
        if p >= 0 and p < end:
            end = p
    v = tail[:end].strip(" :\n\t")
    v = re.sub(r"\s+", " ", v).strip()
    return v


def enrich_with_html_if_needed(session, oc, row, timeout=(5, 20)):
    if row["판시사항"] and row["판결요지"]:
        return row
    pid = row["판례일련번호"]
    if not pid:
        return row
    params = {
        "OC": oc,
        "target": "prec",
        "type": "HTML",
        "ID": pid
    }
    try:
        r = session.get(SERVICE_URL, params=params, timeout=timeout)
        r.raise_for_status()
        txt = clean_text(r.text)
        if not row["판시사항"]:
            row["판시사항"] = extract_section_text(txt, "판시사항")
        if not row["판결요지"]:
            row["판결요지"] = extract_section_text(txt, "판결요지")
    except Exception:
        pass
    return row


def search_candidates(session, oc, query, display=100, timeout=(5, 20)):
    for search_mode in (1, 2):
        params = {
            "OC": oc,
            "target": "prec",
            "type": "JSON",
            "query": query,
            "search": search_mode,
            "display": display,
            "page": 1
        }
        r = session.get(SEARCH_URL, params=params, timeout=timeout)
        r.raise_for_status()
        items = to_items(r.json())
        if items:
            return items, search_mode
    return [], 2


def collect_top5(query, top_k=5):
    load_dotenv()
    oc = os.getenv("LAW_OC_ID", "").strip()
    if not oc:
        raise ValueError("LAW_OC_ID is missing")

    query = query.strip()
    if not query:
        raise ValueError("query is empty")

    save_dir = os.path.dirname(SAVE_PATH)
    if save_dir and not os.path.isdir(save_dir):
        raise FileNotFoundError(f"save directory not found: {save_dir}")

    session = build_session()
    raw_items, used_search = search_candidates(session, oc, query, display=100, timeout=(5, 20))

    seen_pid = set()
    cands = []

    for it in raw_items:
        row = map_row(it)
        row = enrich_with_html_if_needed(session, oc, row, timeout=(5, 20))

        pid = row["판례일련번호"]
        if not pid or pid in seen_pid:
            continue
        seen_pid.add(pid)

        sc = weighted_score(query, row)
        cands.append((sc, row))

    cands.sort(key=lambda x: -x[0])
    top_rows = [x[1] for x in cands[:top_k]]

    result = {
        "query": query,
        "used_search": used_search,
        "count": len(top_rows),
        "collected_at": datetime.now().isoformat(timespec="seconds"),
        "results": top_rows
    }

    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


if __name__ == "__main__":
    q = input("키워드 입력: ").strip()
    if not q:
        raise ValueError("query is empty")
    out = collect_top5(q, top_k=5)
    print(f"saved={out['count']} path={SAVE_PATH} used_search={out['used_search']}")
















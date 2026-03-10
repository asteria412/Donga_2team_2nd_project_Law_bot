import datetime, time, requests, xml.etree.ElementTree as ET, re
from config.settings import API_KEY, BASE_URL_LAW, BASE_URL_SERVICE, HEADERS
import streamlit as st

def get_law_change_summary(mst_id, session):
    try:
        params = {'OC': API_KEY,'target': 'oldAndNew','MST': mst_id,'type': 'XML'}
        res = session.get(BASE_URL_SERVICE, params=params, timeout=10)
        res.raise_for_status()
        root = ET.fromstring(res.text)
        pattern = re.compile(r'제\d+조\(.*?\)')
        for elem in root.iter():
            if elem.text:
                m = pattern.search(elem.text)
                if m:
                    return f"📍 {m.group()} 등 개정"
        return ""
    except:
        return ""

def get_laws_sync(dept, count):
    DEPT_KEYWORDS = {
        "인사팀": ["근로기준법","남녀고용평등","산업안전보건법","최저임금법","근로자퇴직급여","파견근로자"],
        "총무팀": ["개인정보 보호법","상법","부정청탁","독점규제 및 공정거래","하도급거래"],
        "재무팀": ["법인세법","부가가치세법","조세특례제한법","자본시장과 금융투자업에 관한 법률","상법"]
    }
    curr_kw = DEPT_KEYWORDS.get(dept, sum(DEPT_KEYWORDS.values(), []))
    EXCLUDE_KEYWORDS = ["공무원","군인","군용","군사","민주화운동","직제","소속기관","교육감","교원","지방의회","정부조직"]

    all_raw = []
    ninety_days_ago = (datetime.datetime.now() - datetime.timedelta(90)).strftime('%Y%m%d')
    session = requests.Session()
    session.headers.update(HEADERS)

    for kw in curr_kw:
        for attempt in range(2):
            try:
                time.sleep(0.5)
                res = session.get(BASE_URL_LAW,
                    params={'target':'oldAndNew','type':'XML','OC':API_KEY,'query':kw},timeout=15)
                res.raise_for_status()

                root = ET.fromstring(res.text)
                for item in root.findall('.//oldAndNew'):
                    name = item.findtext('신구법명','')
                    if any(e in name for e in EXCLUDE_KEYWORDS): continue
                    if "사립학교" in name or "국가정보원" in name: continue

                    p_dt = item.findtext('공포일자','')
                    e_dt = item.findtext('시행일자','')
                    if p_dt >= ninety_days_ago or e_dt >= ninety_days_ago:
                        dept_tag = "🗂️ 기타/공통"
                        for d_n, kws in DEPT_KEYWORDS.items():
                            if any(k in name for k in kws):
                                dept_tag = f"📍 {d_n.replace('팀','')}/회계팀" if "재무" in d_n else f"📍 {d_n}"

                        summary = get_law_change_summary(item.findtext('신구법일련번호',''), session)

                        all_raw.append({
                            "title": name, "p_dt": p_dt, "e_dt": e_dt,
                            "agency": item.findtext('소관부처명',''),
                            "mst_id": item.findtext('신구법일련번호',''),
                            "dept": dept_tag, "summary": summary
                        })
                break
            except Exception:
                time.sleep(1)
                continue

    unique = {l['mst_id']: l for l in all_raw}.values()
    return sorted(unique, key=lambda x: x['p_dt'], reverse=True)

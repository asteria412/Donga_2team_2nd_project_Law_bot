""" logic/summarizer.py
[AI 기반 법령 퀴즈 생성기] 최신 개정 법령의 상세 조문을 분석하여 실무 맞춤형 퀴즈를 생성하는 파일입니다.
단순히 법령 내용을 요약하는 수준을 넘어, OpenAI LLM을 활용해 실제 비즈니스 시나리오(인사/재무/총무)에 기반한 
4지선다형 문제를 출제하며, 사용자에게 구체적인 실무 Action Item과 해설을 제공하는 교육 엔진 역할을 수행합니다. """

import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

from utils.token import update_token_usage

# .env 파일에서 환경변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화 (API 키는 환경변수 OPENAI_API_KEY에서 자동 로드됨)
client = OpenAI()
import streamlit as st

# 캐시 파일 경로
QUIZ_CACHE_FILE = 'data/quiz_cache.json'

def load_quiz_cache():
    if os.path.exists(QUIZ_CACHE_FILE):
        try:
            with open(QUIZ_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_quiz_cache(cache):
    os.makedirs(os.path.dirname(QUIZ_CACHE_FILE), exist_ok=True)
    with open(QUIZ_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

@st.cache_data(show_spinner=False)
def generate_quiz_from_ai(law_data, question_idx=0, count=3):
    """
    주어진 법령 데이터(딕셔너리)를 바탕으로 OpenAI LLM을 사용하여 여러 개의 4지선다형 퀴즈를 일괄 생성합니다.
    """
    if not law_data:
        return None
        
    law_name = law_data.get('law_name', '알 수 없는 법령')
    enf_dt = law_data.get('enf_dt', '')
    
    mst_id = law_data.get('mst_id', '')
    
    # [핵심 로직 혁신] aiSearch 대신 100% 본문을 보장하는 'lawService.do(신구법 본문조회 API)'를 사용합니다!
    article_title = "신구법 개정 조문"
    article_content = "상세 법령 텍스트 조회 실패. (※주의: AI, 조문 내용이 없더라도 절대 날짜나 소관부처를 묻지 말고, 이 법의 대표적인 실무 사례나 일반적인 직무 상식을 묻는 가상의 퀴즈를 출제할 것!)"
    
    if mst_id:
        try:
            import xml.etree.ElementTree as ET
            safe_api_key = os.getenv("LAW_API_KEY", "")
            service_params = {
                'target': 'oldAndNew',
                'type': 'XML',
                'OC': safe_api_key,
                'MST': mst_id
            }
            res = requests.get('http://www.law.go.kr/DRF/lawService.do', params=service_params)
            res.raise_for_status()
            res.encoding = 'utf-8'
            
            root = ET.fromstring(res.text)
            
            # 신조문목록 아래의 조문 텍스트를 긁어옵니다.
            new_articles = root.findall('.//신조문목록/조문')
            if not new_articles:
                # 혹시 신조문이 비었다면 전체 조문을 무식하게 긁습니다.
                new_articles = root.findall('.//조문')

            if new_articles:
                extracted_texts = []
                for idx, article in enumerate(new_articles):
                    text = "".join(article.itertext()).strip()
                    if text:
                        extracted_texts.append(text)
                
                if extracted_texts:
                    article_content = "\n".join(extracted_texts)[:1500] # 조금 더 길게 정보 제공
        except Exception as e:
            print(f"조문 본문 100% 딥서치 중 오류 발생 (무시하고 상식 퀴즈로 진행): {e}")

    # [CACHING] 이미 생성된 퀴즈가 있는지 확인
    cache = load_quiz_cache()
    cache_key = f"{mst_id}_{law_name}"
    if cache_key in cache and len(cache[cache_key]) > question_idx:
        return cache[cache_key] # 리스트 전체 반환

    # 실제 조문 내용을 바탕으로 실무 퀴즈를 짜도록 프롬프트 강화!
    prompt = f"""
    당신은 기업의 실무진(인사, 재무, 총무)을 교육하는 직무 교육 퀴즈 출제 위원입니다.
    이번 출제 대상 법령 정보는 다음과 같습니다.
    
    - 대상 법령: {law_name}
    - 상세 조문내용: {article_content}
    
    위 '상세 조문내용'을 바탕으로, 실무에서 마주칠 법한 시나리오 기반의 4지 선다형 퀴즈를 총 {count}문제 생성하세요.
    각 문제는 서로 다른 조문이나 포인트를 다루어야 합니다.

    [출제 철칙]
    1. ❌ 단순 암기 질문 금지: '공포일', '시행일', '소관부처' 질문은 절대 금지!
    2. ❌ 조문 번호 보기 금지: 보기(Options)에 "제206조" 처럼 **조문 번호만 넣는 것은 절대 금지**입니다. 보기는 반드시 구체적인 설명이나 수치가 포함된 문장이어야 합니다.
    3. ✅ 가상 시나리오 활용: 질문은 가상의 실무 상황("무한개발공사 인사팀의 김대리가 ~하려고 한다")으로 구성하세요.
    4. ✅ 해설에는 근거 조문과 실무 Action Item을 포함하세요.
    5. ⚠️ 정답 필드: 'answer' 필드에는 반드시 위 'options' 리스트에 있는 문자열과 **토씨 하나 틀리지 않고 똑같은 문자열**을 넣으세요.
    
    반드시 아래 견본 리스트 형식의 순수 JSON으로만 응답하세요. (마크다운 없이)
    [
        {{
            "question": "가상의 실무 질문 1...",
            "options": ["정확한 답변 문장1", "정확한 답변 문장2", "정확한 답변 문장3", "정확한 답변 문장4"],
            "answer": "정확한 답변 문장1",
            "explanation": "해설 1..."
        }},
        ... (총 {count}개)
    ]
    """
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a specialized corporate Scenario-based Quiz Generator. You EXCLUSIVELY create practical business scenario multiple-choice questions. You NEVER ask for trivia like dates, departments, or names."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
            )
            update_token_usage(response.usage)
            quiz_json_str = response.choices[0].message.content.strip()
            
            # 기계적인 JSON 파싱 보호 구문(.strip() 및 마크다운 제거)
            if quiz_json_str.startswith('```json'):
                quiz_json_str = quiz_json_str[7:]
            if quiz_json_str.endswith('```'):
                quiz_json_str = quiz_json_str[:-3]
                
            quiz_list = json.loads(quiz_json_str.strip())
            
            if not isinstance(quiz_list, list):
                quiz_list = [quiz_list]

            # 가드레일: 날짜/부처 질문 제거
            valid_quiz_list = []
            bad_keywords = ["소관부처는", "어디인가", "공포일은", "시행일은", "날짜는", "언제인가"]
            
            for q_data in quiz_list:
                combined_text = q_data.get("question", "") + " ".join(q_data.get("options", []))
                check_text = combined_text.replace(law_name, "")
                if not any(word in check_text for word in bad_keywords):
                    valid_quiz_list.append(q_data)

            if len(valid_quiz_list) > 0:
                # 캐시에 저장
                cache[cache_key] = valid_quiz_list
                save_quiz_cache(cache)
                return valid_quiz_list
                
            continue
            
        except Exception as e:
            print(f"퀴즈 생성 중 오류 발생 (시도 {attempt+1}/3): {e}")
            continue

    # 최종 비상용 퀴즈 (리스트 형태)
    emergency_quiz = [{
        "question": f"무한개발공사 경영지원본부가 '{law_name}' 업데이트와 관련하여 가장 먼저 취해야 할 올바른 실무 조치는 무엇일까요?",
        "options": ["사내 취업규칙 및 기안 규정 점검", "아무 조치 없이 관행대로 업무 진행", "사장님에게 구두로만 임의 보고", "전 직원 즉각 조기 퇴근"],
        "answer": "사내 취업규칙 및 기안 규정 점검",
        "explanation": "법령이 개정될 때는 우리 회사의 취업규칙과 내부 정책이 위반되지 않는지 선제적으로 점검하는 것이 실무의 기본입니다!"
    }]
    return emergency_quiz

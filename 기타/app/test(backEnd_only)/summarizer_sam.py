import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 환경변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화 (API 키는 환경변수 OPENAI_API_KEY에서 자동 로드됨)
client = OpenAI()

def generate_quiz_from_ai(law_data):
    """
    주어진 법령 데이터(딕셔너리)를 바탕으로 OpenAI LLM을 사용하여 4지선다형 퀴즈를 생성합니다.
    출력은 반드시 JSON 문자열 형태여야 합니다.
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
                # 개정된 조문이 여러 개일 수 있으므로 텍스트를 추출해 합칩니다.
                extracted_texts = []
                for idx, article in enumerate(new_articles):
                    text = "".join(article.itertext()).strip()
                    if text:
                        extracted_texts.append(text)
                
                if extracted_texts:
                    # 너무 길면 LLM 토큰비가 폭발하고 AI가 헷갈려하므로 1000자로 타이트하게 컷!
                    article_content = "\n".join(extracted_texts)[:1000]
        except Exception as e:
            print(f"조문 본문 100% 딥서치 중 오류 발생 (무시하고 상식 퀴즈로 진행): {e}")

    # 실제 조문 내용을 바탕으로 실무 퀴즈를 짜도록 프롬프트 강화!
    prompt = f"""
    당신은 기업의 실무진(인사, 재무, 총무)을 교육하는 직무 교육 퀴즈 출제 위원입니다.
    이번 출제 대상 법령 정보는 다음과 같습니다.
    
    - 대상 법령: {law_name}
    - 참고 조문제목: {article_title}
    - 상세 조문내용: {article_content}
    
    위 '상세 조문내용'을 꼼꼼히 읽고, 조문에 실제로 명시된 구체적인 숫자, 기준, 금액, 비율, 기간, 자격 조건 등을 활용하여 실무 퀴즈 1문제를 4지 선다형으로 출제하세요.

    [출제 철칙 - 반드시 지킬 것]
    1. ❌ 메타데이터 질문 금지: '공포일은?', '시행일은?', '소관부처는?' 같은 단순 암기 질문은 절대 금지!
    2. ❌ 추상적 보기 금지: '관련 교육을 실시한다', '규정을 업데이트한다', '목록을 갱신한다' 같은 누구나 맞출 수 있는 뻔한 보기는 ❌감점❌입니다!
    3. ✅ 조문 기반 구체적 보기 필수: 보기에는 반드시 조문에 나오는 실제 숫자·기준·비율·기간·금액을 포함하세요. 예) "연 100분의 40 이내의 이율", "14일 이내", "30인 이상 사업장" 등.
    4. ✅ 오답 보기는 조문의 숫자를 살짝 바꿔서(예: 14일→30일, 40%→20%) 헷갈리게 만드세요.
    5. ✅ 질문은 가상의 실무 상황("무한개발공사 인사팀의 김대리가 ~하려고 한다")으로 시작하세요.
    6. ✅ 해설에는 근거 조문을 인용하고 실무 Action Item을 포함하세요.
    
    반드시 아래 견본과 똑같은 형식의 순수 JSON으로만 응답하세요. (마크다운 코드블록 불허)
    {{
        "question": "무한개발공사 인사팀의 김대리가 퇴직한 직원의 미지급 임금 처리 기준을 확인하려 합니다. '{law_name}'에 따른 지연이자 이율 상한은?",
        "options": ["연 100분의 20 이내", "연 100분의 40 이내", "연 100분의 50 이내", "연 100분의 60 이내"],
        "answer": "연 100분의 40 이내",
        "explanation": "제37조에 따르면 미지급 임금에 대한 지연이자는 '연 100분의 40 이내'로 규정되어 있습니다. (Action Item: 급여팀에 지연이자율 적용 기준표를 배포하세요.)"
    }}
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
            
            quiz_json_str = response.choices[0].message.content.strip()
            
            # 기계적인 JSON 파싱 보호 구문(.strip() 및 마크다운 제거)
            if quiz_json_str.startswith('```json'):
                quiz_json_str = quiz_json_str[7:]
            if quiz_json_str.endswith('```'):
                quiz_json_str = quiz_json_str[:-3]
                
            quiz_data = json.loads(quiz_json_str.strip())
            
            # [최종 방어 로직] LLM이 날짜/부처를 물어봤는지 체크
            # 💡 주의: '시행', '공포'는 법령명("시행령", "시행규칙")에 포함될 수 있으므로 제거!
            bad_keywords = ["소관부처는", "어디인가", "공포일은", "시행일은", "날짜는", "언제인가"]
            combined_text = quiz_data.get("question", "") + " ".join(quiz_data.get("options", []))
            # 법령명을 검사 텍스트에서 제거 (법령명에 '시행'이 들어가면 오탐 방지)
            check_text = combined_text.replace(law_name, "")
            
            is_bad = any(word in check_text for word in bad_keywords)
            
            if is_bad:
                print(f"[GUARD {attempt+1}] AI asked meta-data. Retrying...")
                continue
                
            return quiz_data # 룰 통과 시 즉시 반환
            
        except Exception as e:
            print(f"퀴즈 생성 중 오류 발생 (시도 {attempt+1}/3): {e}")
            continue

    # 3번이나 AI가 말을 안들었거나 에러가 났을 때 나오는 '최후의 비상용 상식 퀴즈'
    return {
        "question": f"무한개발공사 경영지원본부가 '{law_name}' 업데이트와 관련하여 가장 먼저 취해야 할 올바른 실무 조치는 무엇일까요?",
        "options": ["사내 취업규칙 및 기안 규정 점검", "아무 조치 없이 관행대로 업무 진행", "사장님에게 구두로만 임의 보고", "전 직원 즉각 조기 퇴근"],
        "answer": "사내 취업규칙 및 기안 규정 점검",
        "explanation": "법령이 개정될 때는 우리 회사의 취업규칙과 내부 정책이 위반되지 않는지 선제적으로 점검하는 것이 실무의 기본입니다!"
    }

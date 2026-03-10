import json
from dotenv import load_dotenv
from openai import OpenAI

# 환경변수 로드
load_dotenv()
client = OpenAI()

def predict_department_with_ai(law_name, dept_nm):
    """
    법령명과 소관부처를 바탕으로 OpenAI LLM에게 질문하여, 
    해당 법령을 다뤄야 할 가장 적합한 경영지원본부 내 팀을 '추론'합니다.
    """
    prompt = f"""
    당신은 10년 차 대기업 법무/컴플라이언스 초특급 분류 AI입니다.
    새로운 법령(개정안 등)이 발표되었습니다.
    
    - 대상 법령명: {law_name}
    - 해당 소관부처: {dept_nm}
    
    이 법령의 성격을 추론하여, 무한개발공사 '경영지원본부'의 아래 3개 팀 중 어느 팀이 실무를 담당하는 것이 가장 적합할지 단 1개의 팀만 선택하세요.
    
    [분류 후보 및 판단 기준]
    1. 인사팀 (근로기준, 안전, 채용, 조직, 노사, 보훈, 연금 등 직원과 관련된 모든 것)
    2. 총무팀 (보안, 정보보호, 회사 인프라, 이사회, 공정거래, 계약, 기업일반, 법무, 환경보건 등)
    3. 재무팀 (세금, 회계, 예산, 금융, 외국환, 펀드, 보조금, 관세 등 금전 및 숫자와 관련된 모든 것)
    4. 기타 (위 3개 부서와 전혀 일도 무관한 법군사, 해양, 우주, 교육 등)
    
    오직 아래와 같은 순수 JSON 형식으로만 대답하세요. 다른 부가 설명은 절대 금지합니다.
    {{
        "team": "총무팀"
    }}
    (team 값은 무조건 "인사팀", "총무팀", "재무팀", "기타" 중 하나여야 합니다.)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict JSON-only classifier."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0, # 분류 문제이므로 창의성 0으로 고정
        )
        
        result_str = response.choices[0].message.content.strip()
        
        # 기계적인 마크다운 찌꺼기 제거
        if result_str.startswith('```json'):
            result_str = result_str[7:]
        if result_str.endswith('```'):
            result_str = result_str[:-3]
            
        data = json.loads(result_str.strip())
        team_str = data.get("team", "기타")
        
        # 내부 분류망 매핑 코드로 변환
        if "인사" in team_str:
            return "👥 인사/HR팀"
        elif "총무" in team_str:
            return "🏢 총무팀"
        elif "재무" in team_str:
            return "💼 재무/회계팀"
        else:
            return "🗂️ 기타/공통"
            
    except Exception as e:
        print(f"[ERROR] AI Tagging error: {e}")
        return "🗂️ 기타/공통"

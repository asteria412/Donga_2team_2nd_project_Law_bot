import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

# 1. 환경 변수 로드
load_dotenv()

class LawAnalyzer:
    def __init__(self):
        # 과제 요구사항: gpt-4o-mini 사용
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def _extract_department_by_regex(self, text: str):
        """정규표현식을 이용한 빠른 정부 부서명 추출"""
        match = re.search(r"(?:담당부서|주관부서|소관부서)\s*[:：]\s*([가-힣\s]+?)(?:\r|\n|[(]|$)", text)
        if match:
            return match.group(1).strip()
        return None

    def extract_tags(self, text: str):
        """법령에서 부서명, 사내 분류, 키워드를 추출하는 기능"""
        regex_dept = self._extract_department_by_regex(text)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 가상 회사 '경영지원본부'의 AI 법무 어시스턴트입니다. 
법령 텍스트를 분석하여 아래 JSON 형식으로 응답하세요:
{{
  "gov_department": "정부 주관 부서 (없으면 '미지정')",
  "company_category": "사내 관련 부서 (인사/HR, 재무/회계, 총무, 기타 중 택1)",
  "keywords": ["핵심키워드1", "핵심키워드2", "핵심키워드3"]
}}
참고(Regex 추출 결과): {dept_hint}"""),
            ("human", "분석할 법령 텍스트:\n{law_text}")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        return chain.invoke({
            "law_text": text,
            "dept_hint": regex_dept if regex_dept else "없음"
        })

    def compare_laws(self, old_text: str, new_text: str):
        """이전/이후 법령의 차이점을 분석하여 기업 조치 사항을 제안하는 기능"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 기업 경영지원본부 소속의 법령 개정 분석 전문가입니다. 
법령 개정안을 기업 관점에서 분석하여 Markdown 보고서 형태로 답변하세요. 

### 1. 개정 요약 및 취지
- 기업 입장에서 어떤 점이 바뀌는지 한 줄 요약

### 2. 주요 변경 대비 (Before vs After)
- 구체적인 규정 변화를 항목별로 비교

### 3. 🚨 기업 준수 사항 및 조치 필요 항목
- 우리 회사가 즉시 수행해야 할 액션 아이템 (예: 취업규칙 개정, 시스템 반영 등)
- 관련 부서(인사/재무/총무)별 권고 사항"""),
            ("human", "이전 규정:\n{old}\n\n현재 규정:\n{new}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"old": old_text, "new": new_text})

# --- 경영지원본부 맞춤형 테스트 섹션 ---
if __name__ == "__main__":
    analyzer = LawAnalyzer()
    
    # 예시 1: 인사/HR 관련 (근로기준법 개정 가정)
    hr_law = """
    [공포일: 2026.03.01] 제53조(연장 근로의 제한) 
    사용자는 특별한 사정이 있으면 고용노동부장관의 승인과 근로자의 동의를 받아 연장근로를 시킬 수 있다.
    [담당부서: 고용노동부 근로기준정책과]
    """
    
    print("="*60)
    print(" [Case 1. HR 관련 법령 태깅 및 부서 분류] ")
    print("="*60)
    hr_tags = analyzer.extract_tags(hr_law)
    print(f"결과: {hr_tags}")
    
    # 예시 2: 재무/회계 관련 (세법 개정 가정)
    old_tax = "법인세율을 과세표준 2억원 이하에 대해 10%를 적용한다."
    new_tax = "법인세율을 과세표준 5억원 이하에 대해 9%를 적용하여 중소기업의 부담을 완화한다."
    
    print("\n" + "="*60)
    print(" [Case 2. 재무 관련 법령 개정 비교 및 회사 조치 사항] ")
    print("="*60)
    tax_analysis = analyzer.compare_laws(old_tax, new_tax)
    print(tax_analysis)

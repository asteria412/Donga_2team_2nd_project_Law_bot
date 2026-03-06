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
        """법령에서 부서명, 사내 분류, 키워드, 요약, 시행일, 리스크를 추출하는 기능"""
        regex_dept = self._extract_department_by_regex(text)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 가상 회사 '경영지원본부'의 AI 법무 어시스턴트입니다. 
법령 텍스트를 분석하여 아래 JSON 형식으로 응답하세요. 
이 데이터는 사내 DB에 저장되어 대시보드와 업데이트 목록에 바로 사용됩니다:
{{
  "law_title": "법령 명칭 (예: 근로기준법)",
  "article_title": "조문 제목 (예: 제53조 연장 근로의 제한)",
  "gov_department": "정부 주관 부서 (예: 고용노동부)",
  "related_departments": ["사내 관련 부서 (인사/HR, 재무/회계, 총무 중 선택)"],
  "summary": "법령 요약 (변경 사항이 많을 경우 '제n조 [제목] 외 m건 변동' 형식으로 시작하고, 뒤에 핵심 변경 취지를 1~2문장으로 덧붙이세요)",
  "article_changes": {{
    "added": ["제n조", "제m조"],
    "deleted": ["제k조"],
    "modified": ["제p조", "제q조"]
  }},
  "announcement_date": "공포일 (YYYY-MM-DD, 없으면 '미정')",
  "effective_date": "시행일 (YYYY-MM-DD, 없으면 '미정')",
  "risk_level": "리스크 등급 (상, 중, 하)",
  "keywords": ["핵심키워드1", "핵심키워드2"]
}}

**[사내 부서 분류 가이드]**
1. **인사(HR)**: 근로기준법, 산업안전보건법, 남녀고용평등법 등
2. **재무(Finance)**: 상법(회계), 법인세법, 조세특례제한법, 부가가치세법 등
3. **총무(General Affairs)**: 상법(주총/이사), 공정거래법, 개인정보보호법 등

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

### 1. 📂 조문 변동 현황 (핵심 요약)
- **추가**: 제n조, 제m조 ... (3개 초과 시 '등'으로 표시)
- **삭제**: 제k조 ...
- **변경**: 제p조 ...

### 2. 📝 개정 요약 및 취지
- 기업 입장에서 어떤 점이 바뀌는지 한 줄 요약

### 3. 🔍 주요 변경 대비 (Before vs After)
- 구체적인 규정 변화를 항목별로 비교

### 4. 🚨 기업 준수 사항 및 조치 필요 항목
- 우리 회사가 즉시 수행해야 할 액션 아이템 (예: 취업규칙 개정, 시스템 반영 등)
- 관련 부서(인사/재무/총무)별 권고 사항
- 수정이 필요한 사내 규정 목록 추천"""),
            ("human", "이전 규정:\n{old}\n\n현재 규정:\n{new}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"old": old_text, "new": new_text})

    def analyze_crawler_data(self, crawler_json: dict):
        """크롤러가 수집한 JSON 데이터를 받아 전체 분석(태깅+비교)을 수행하는 브릿지 함수"""
        detail = crawler_json.get("OldAndNewService", {})
        
        # 1. 방어적 필드 추출 (언더바 포함/미포함 대응)
        def get_field(obj, keys):
            for k in keys:
                if k in obj: return obj[k]
            return {}

        new_info = get_field(detail, ["신조문_기본정보", "신조문기본정보"])
        old_info = get_field(detail, ["구조문_기본정보", "구조문기본정보"])
        
        new_list_obj = get_field(detail, ["신조문목록", "신조문_목록"])
        old_list_obj = get_field(detail, ["구조문목록", "구조문_목록"])
        
        new_items = new_list_obj.get("조문", [])
        old_items = old_list_obj.get("조문", [])
        
        new_text = "\n".join([item.get("content", "") for item in new_items])
        old_text = "\n".join([item.get("content", "") for item in old_items])
        
        # 2. 기본 정보 구성 (태깅 및 비교 힌트용)
        law_context = f"""법령명: {new_info.get('법령명', '')}
공포일: {new_info.get('공포일자', '')}
시행일: {new_info.get('시행일자', '')}
개정구분: {new_info.get('제개정구분명', '')}
소관부처: {new_info.get('소관부처명', '')}

[신조문]
{new_text}

[구조문]
{old_text}"""
        
        # 3. AI 분석 수행
        tags = self.extract_tags(law_context)
        comparison = self.compare_laws(old_text, new_text)
        
        return {
            "tags": tags,
            "comparison_report": comparison
        }

    def analyze_precedent(self, text: str):
        """판례 본문을 분석하여 핵심 키워드, 사건 요약, 기업 시사점을 추출하는 기능"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 기업 법무팀 소속의 판례 분석 전문가입니다. 
판례 내용을 분석하여 아래 JSON 형식으로 응답하세요:
{{
  "case_name": "사건명",
  "case_number": "사건번호",
  "keywords": ["핵심키워드1", "핵심키워드2", "핵심키워드3"],
  "summary": "판결 요지 및 핵심 내용 요약",
  "corporate_implication": "우리 회사에 주는 시사점 및 주의 사항 (경영지원 관점)"
}}"""),
            ("human", "분석할 판례 텍스트:\n{precedent_text}")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        return chain.invoke({"precedent_text": text})

    def answer_with_rag(self, query: str, context: str):
        """RAG로 검색된 참고 자료(context)를 바탕으로 사용자의 질문에 답하는 기능 (챗봇 엔진)"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 기업 경영지원본부의 법무 에이전트입니다. 
제공된 [참고 법령 및 판례 자료]를 바탕으로 사용자의 질문에 정확하고 전문적으로 답변하세요. 
답변에는 반드시 관련 법령이나 판례의 출처를 명시해야 합니다.

[참고 자료]
{context}"""),
            ("human", "{query}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"query": query, "context": context})

# --- 경영지원본부 맞춤형 테스트 섹션 ---
if __name__ == "__main__":
    analyzer = LawAnalyzer()
    
    # 예시 3: 팀원들의 실제 크롤러 데이터 연동 테스트
    print("\n" + "="*60)
    print(" [Case 3. 실제 크롤러 JSON 데이터 연동 테스트] ")
    print("="*60)
    
    # 실제 샘플 데이터 로드 (파일이 없을 경우 대비하여 try-except)
    import json
    sample_path = "app/api/sample_law_versions_detail.json"
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            sample_json = json.load(f)
        
        analysis_result = analyzer.analyze_crawler_data(sample_json)
        
        print("\n[1. 태깅 및 분류 결과]")
        print(json.dumps(analysis_result["tags"], ensure_ascii=False, indent=2))
        
        print("\n[2. 개정 비교 보고서]")
        print(analysis_result["comparison_report"])
        
    except FileNotFoundError:
        print(f"❌ '{sample_path}' 파일을 찾을 수 없어 테스트를 건너뜁니다.")

    print("\n" + "="*60)
    print(" [Case 4. 실제 판례 JSON 데이터 연동 테스트] ")
    print("="*60)
    
    prec_path = "app/test(backEnd_only)/output/law_prec.json"
    try:
        with open(prec_path, "r", encoding="utf-8") as f:
            prec_json = json.load(f)
        
        # 실제 데이터에서 판결요지 추출
        judgment_text = prec_json.get("본문결과", {}).get("판결요지", "")
        
        if judgment_text:
            print(f"\n[대상 판례]: {prec_json.get('판례명', '알 수 없음')}")
            precedent_result = analyzer.analyze_precedent(judgment_text)
            print(json.dumps(precedent_result, ensure_ascii=False, indent=2))
        else:
            print("⚠️ 판례 본문 데이터가 없어 테스트를 수행할 수 없습니다.")
            
    except FileNotFoundError:
        print(f"❌ '{prec_path}' 파일을 찾을 수 없어 테스트를 건너뜁니다.")

    # 예시 5: RAG 연동 가상 테스트 (챗봇 모드)
    print("\n" + "="*60)
    print(" [Case 5. RAG 기반 지식 답변 테스트 (챗봇)] ")
    print("="*60)
    
    # RAG 리트리버가 찾아준 가상의 컨텍스트 데이터
    mock_context = """
    [문서 1 - 출처: 근로기준법 제60조]
    사용자는 1년간 80퍼센트 이상 출근한 근로자에게 15일의 유급휴가를 주어야 한다.
    [문서 2 - 출처: 근로기준법 제61조]
    사용자가 유급휴가 사용을 촉진하기 위한 조치를 하였음에도 근로자가 휴가를 사용하지 아니한 경우, 사용자는 그 미사용 휴가에 대하여 보상할 의무가 없다.
    """
    user_query = "회사가 연차 사용을 독촉했는데도 제가 안 쓰면 돈으로 못 받나요?"
    
    rag_response = analyzer.answer_with_rag(user_query, mock_context)
    print(f"질문: {user_query}")
    print(f"답변:\n{rag_response}")

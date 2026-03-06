""" app/rag/retriever.py
[데이터 검색 엔진] 사용자가 질문을 던지면, 디지털 창고에서 가장 관련 있는 지식을 쏙쏙 찾아오는 역할을 합니다.
질문과 가장 의미가 비슷한 조각들을 골라내어 AI가 정확한 법률 답변을 할 수 있도록 근거 자료를 제공합니다."""

import os
from typing import List, Dict
from langchain_core.documents import Document
from app.rag.embedder import embedder_instance

class HRRetriever:
    def __init__(self):
        self.vectorstore = embedder_instance.get_vectorstore()
        
    def get_relevant_documents(self, query: str, user_dept: str = "General", k: int = 3) -> List[Document]:
        """
        권한(user_dept)에 기반한 Metadata Filtering 검색 수행
        """
        if not self.vectorstore or not os.path.exists("data/vector_db"):
            print("Vector DB is missing. Returning empty list.")
            return []
            
        # TODO: 실제 Metadata Filtering (Self-Query 리트리버 적용)
        # 예시: retriever = self.vectorstore.as_retriever(search_kwargs={'k': k, 'filter': {'category': 'HR Policy'}})
        retriever = self.vectorstore.as_retriever(search_kwargs={'k': k})
        
        try:
            docs = retriever.invoke(query)
            return docs
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []
            
    def format_docs_with_citation(self, docs: List[Document]) -> str:
        """
        RAG 성능 강화 및 신뢰성 확보를 위한 Citation (출처 표시) 포맷터
        LLM에게 던져줄 Context 문자열을 생성하며, 각 청크의 메타데이터 source를 강제로 각인.
        """
        formatted_context = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown Source")
            content = doc.page_content.replace('\n', ' ')
            formatted_context.append(f"[문서 {i+1} - 출처: {source}]\n{content}\n")
            
        return "\n".join(formatted_context)

retriever_instance = HRRetriever()
"""
if __name__ == "__main__":
    # 1. 아까 저장한 '건설업 수급인 임금 지급 책임'에 대한 질문을 던집니다.
    test_query = "건설업에서 하수급인이 임금을 못 주면 누가 책임져야 하나요?"
    
    # 2. 관련 문서 3개 찾아오기 (저장했던 조각이 나올 거예요!)
    found_docs = retriever_instance.get_relevant_documents(test_query, k=3)
    
    # 3. 출처(판례명, 사건번호 등)가 잘 나오도록 출력 포맷을 확인합니다.
    # 메타데이터 키값이 "판례명", "사건번호"로 저장되었으므로 이를 반영해 출력하면 더 좋습니다.
    print(f"\n🔎 질문: {test_query}")
    print("-" * 50)
    
    if not found_docs:
        print("❌ 검색된 결과가 없습니다. DB 저장 상태를 확인해 주세요.")
    else:
        for i, doc in enumerate(found_docs):
            title = doc.metadata.get("판례명", "정보 없음")
            case_no = doc.metadata.get("사건번호", "정보 없음")
            print(f"📄 [결과 {i+1}] {title} ({case_no})")
            print(f"💡 내용 요약: {doc.page_content[:150]}...") # 앞부분만 살짝 출력
            print("-" * 50)
            """
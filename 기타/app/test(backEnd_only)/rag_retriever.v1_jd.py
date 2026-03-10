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

# app/rag/retriever.py 맨 밑에 추가

if __name__ == "__main__":
    # 1. 리트리버 인스턴스에서 질문 던지기
    test_query = "전자세금계산서 세액공제에 대해 알려줘"
    
    # 2. 관련 문서 3개 찾아오기
    found_docs = retriever_instance.get_relevant_documents(test_query, k=3)
    
    # 3. 출처와 함께 출력하기
    context = retriever_instance.format_docs_with_citation(found_docs)
    
    print(f"\n🔎 질문: {test_query}")
    print(f"📄 검색된 결과:\n{context}")
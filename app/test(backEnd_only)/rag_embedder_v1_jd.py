""" 이 파일의 기능
[데이터 저장소 구축] 법령이나 규정 같은 텍스트 지식을 AI가 이해할 수 있는 숫자(벡터)로 변환합니다.
변환된 숫자는 'Chroma'라는 디지털 창고에 차곡차곡 쌓여, 나중에 챗봇이 답변할 때 참고서로 쓰입니다."""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.api.dependency import get_settings

class HREmbedder:
    def __init__(self, persist_directory: str = "data/vector_db"):
        self.persist_directory = persist_directory
        self.settings = get_settings()
        
        # 보안 규칙: OPENAI_API_KEY는 .env에서 끌어옴
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", 
            openai_api_key=self.settings.openai_api_key
        )
        
    def get_vectorstore(self) -> Chroma:
        """
        Chroma Vector DB 인스턴스 반환. 데이터가 없으면 None이 할당될 수 있음.
        """
        return Chroma(
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        
    def ingest_documents(self, documents):
        """
        문서들을 받아 벡터 DB에 적재 (초기 1회 또는 업데이트 시 실행)
        """
        if not documents:
            print("No documents to ingest.")
            return None
            
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print(f"Successfully ingested {len(documents)} document chunks into {self.persist_directory}")
        return vectorstore

embedder_instance = HREmbedder()

""" app/rag/embedder.py
[데이터 저장소 구축] 법령이나 규정 같은 텍스트 지식을 AI가 이해할 수 있는 숫자(벡터)로 변환합니다.
변환된 숫자는 'Chroma'라는 디지털 창고에 차곡차곡 쌓여, 나중에 챗봇이 답변할 때 참고서로 쓰입니다."""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 청킹 도구 추가
from app.api.dependency import get_settings

class HREmbedder:
    def __init__(self, persist_directory: str = "data/vector_db"):
        self.persist_directory = persist_directory
        self.settings = get_settings()
        
        # 1. 임베딩 모델 설정 (OpenAI)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", 
            openai_api_key=self.settings.openai_api_key
        )
        
        # 2. 청킹 규칙 설정 (판례 본문을 800자씩 자르고, 80자씩 겹치게 함)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=80,
            length_function=len,
            is_separator_regex=False,
        )
        
    def get_vectorstore(self) -> Chroma:
        """ Chroma Vector DB 인스턴스 반환. """
        return Chroma(
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        
    def ingest_documents(self, documents):
        """ 
        문서들을 받아 '청킹 -> 임베딩 -> 저장' 과정을 한 번에 수행
        """
        if not documents:
            print("❌ 저장할 문서가 없습니다.")
            return None
            
        # [청킹 단계] 긴 문서를 한입 크기로 자릅니다.
        print(f"✂️ {len(documents)}개의 원본 문서를 청킹 중...")
        split_docs = self.text_splitter.split_documents(documents)
        print(f"✅ 청킹 완료: 총 {len(split_docs)}개의 조각으로 나뉘었습니다.")

        # [임베딩 및 저장 단계] 자른 조각들을 숫자로 바꿔 창고에 넣습니다.
        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print(f"💾 성공적으로 {len(split_docs)}개의 조각을 {self.persist_directory}에 저장했습니다.")
        return vectorstore

# 어디서든 불러 쓸 수 있게 인스턴스 생성
embedder_instance = HREmbedder()

# 3. [실행부 추가] 파일 맨 밑에 이 내용을 넣으면 바로 테스트가 가능합니다.
if __name__ == "__main__":
    import json
    from langchain_core.documents import Document

    # 샘플 파일 읽기
    try:
        with open("app/api/sample_law_versions_detail.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 신조문 데이터 추출 및 변환
        new_laws = data["OldAndNewService"]["신조문목록"]["조문"]
        docs = [Document(page_content=item["content"], metadata={"no": item["no"]}) for item in new_laws]

        # 저장 기능 실행
        embedder_instance.ingest_documents(docs)
        print("🎉 DB 저장 성공!")
        
    except FileNotFoundError:
        print("❌ 'sample_law_versions_detail.json' 파일이 없습니다. 파일명을 확인해주세요.")
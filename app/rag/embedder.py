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

"""
# 3. [실행부 추가] 실제 law_prec.json 구조에 맞게 수정했습니다.
if __name__ == "__main__":
    import json
    import re
    from langchain_core.documents import Document

    # 파일 경로 (이미지 및 터미널 확인 경로 기준)
    file_path = "app/test(backEnd_only)/output/law_prec.json"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # [데이터 추출] '본문결과' 내의 '판결요지'를 가져옵니다.
        # <br/> 같은 HTML 태그를 제거하는 전처리 작업을 추가했습니다.
        raw_content = data.get("본문결과", {}).get("판결요지", "")
        clean_content = re.sub(r'<[^>]+>', '', raw_content) # HTML 태그 제거
        
        # [메타데이터 구성] 검색 시 출처로 쓰일 정보들을 정리합니다.
        # 목록결과의 첫 번째 항목에서 사건 정보를 가져옵니다.
        case_info = data.get("목록결과", [{}])[0] 
        
        metadata = {
            "판례명": data.get("판례명", "알 수 없음"),
            "사건번호": case_info.get("사건번호", ""),
            "법원명": case_info.get("법원명", ""),
            "선고일자": case_info.get("선고일자", ""),
            "판례ID": data.get("판례ID", "")
        }

        # [Document 객체 생성] 텍스트와 메타데이터를 하나로 묶습니다.
        if clean_content:
            doc = Document(page_content=clean_content, metadata=metadata)
            
            # 저장 기능 실행 (리스트 형태로 전달)
            embedder_instance.ingest_documents([doc])
            print("🎉 벡터 DB 저장 성공!")
        else:
            print("⚠️ 저장할 본문 내용이 비어있습니다.")
            
    except FileNotFoundError:
        print(f"❌ '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        """
        
        
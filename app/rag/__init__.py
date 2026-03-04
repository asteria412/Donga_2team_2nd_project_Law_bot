"""
RAG(Retrieval-Augmented Generation) 관련 검색/임베딩/리트리벌 로직 패키지.
"""
import os
import json
import fitz  # PyMuPDF: PDF 읽기
import faiss  # Facebook AI: 벡터 유사도 검색
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# 1. 환경 설정 및 경로 지정
load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR = os.path.join(BASE_DIR, "data", "company_docs")  # 사내 표준 PDF 위치
VECTOR_DIR = os.path.join(BASE_DIR, "data", "vectorstore")  # 벡터 창고 저장 위치
INDEX_PATH = os.path.join(VECTOR_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(VECTOR_DIR, "chunks.json")

EMBEDDING_MODEL = "text-embedding-3-small" # 사용할 AI 모델
EMBEDDING_DIM = 1536  # 모델의 숫자 규격

# 2, 3 단계는 사내규정을 업로드 하고 챗봇을 만들때 필수로 필요한 단계이며, 업로드 하지않는다면 생략 가능하다.
# 2. PDF 텍스트 추출 
def extract_text_from_pdfs():
    all_text = []
    if not os.path.exists(DOCS_DIR): return []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".pdf"):
            doc = fitz.open(os.path.join(DOCS_DIR, filename))
            for page_num in range(len(doc)):
                page_text = doc[page_num].get_text()
                if page_text.strip():
                    all_text.append({"source": filename, "page": page_num + 1, "text": page_text.strip()})
            doc.close()
    return all_text

# 3. 청킹 ( 한 입 크기로 쪼개기)
def chunk_text(pages, chunk_size=500, overlap=100):
    chunks = []
    for page in pages:
        text, source, page_num = page["text"], page["source"], page["page"]
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append({"text": chunk.strip(), "source": source, "page": page_num})
            start += chunk_size - overlap
    return chunks

# 4. 임베딩 및 벡터 DB 저장 
def build_index():
    print("[시작] 사내 표준 데이터 수집 및 벡터화...")
    os.makedirs(VECTOR_DIR, exist_ok=True)
    
    # PDF 추출 및 쪼개기
    pages = extract_text_from_pdfs()
    chunks = chunk_text(pages)
    
    # 텍스트를 숫자로 변환 (Embedding)
    client = OpenAI()
    texts = [c["text"] for c in chunks]
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    all_embeddings = [item.embedding for item in response.data]
    
    # 숫자를 창고(FAISS)에 저장
    vectors = np.array(all_embeddings, dtype="float32")
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(vectors)
    
    # 결과 파일 저장
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[완료] {len(chunks)}개의 지식 조각을 창고에 저장했습니다!")

if __name__ == "__main__":
    build_index()
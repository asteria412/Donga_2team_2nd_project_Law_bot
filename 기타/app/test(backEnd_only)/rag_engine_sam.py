"""
============================================
🤖 rag_engine.py - 벡터 RAG 엔진
============================================
사내 규정 PDF를 읽어서 → 청킹 → 임베딩 → FAISS 벡터DB에 저장
챗봇 질문이 들어오면 → 가장 관련 있는 조각을 검색하여 반환

[흐름]
1. build_index()  → PDF 읽기 → 청킹 → 임베딩 → FAISS 저장 (최초 1회)
2. search(query)  → 질문을 임베딩 → FAISS에서 유사 조각 검색 → 텍스트 반환
"""

import os
import json
import fitz  # PyMuPDF: PDF 읽기
import faiss  # Facebook AI: 벡터 유사도 검색
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 💡 경로 설정 (app/agent/ 기준 → 프로젝트 루트로 2단계 올라감)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR = os.path.join(BASE_DIR, "data", "company_docs")
VECTOR_DIR = os.path.join(BASE_DIR, "data", "vectorstore")
INDEX_PATH = os.path.join(VECTOR_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(VECTOR_DIR, "chunks.json")

# 💡 임베딩 모델 (OpenAI text-embedding-3-small: 저렴하고 빠름)
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536  # text-embedding-3-small의 차원 수


# ============================================
# [1단계] PDF에서 텍스트 추출
# ============================================
def extract_text_from_pdfs():
    """data/company_docs/ 폴더의 모든 PDF에서 텍스트를 추출합니다."""
    all_text = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".pdf"):
            filepath = os.path.join(DOCS_DIR, filename)
            doc = fitz.open(filepath)
            page_count = len(doc)
            for page_num in range(page_count):
                page_text = doc[page_num].get_text()
                if page_text.strip():
                    all_text.append({
                        "source": filename,
                        "page": page_num + 1,
                        "text": page_text.strip()
                    })
            doc.close()
            print(f"  [OK] {filename}: {page_count} pages extracted")
    return all_text


# ============================================
# [2단계] 청킹 (Chunking) - 적당한 크기로 자르기
# ============================================
def chunk_text(pages, chunk_size=1000, overlap=200):
    """
    페이지별 텍스트를 chunk_size 글자 단위로 자릅니다.
    overlap: 앞뒤 문맥이 끊기지 않도록 겹치는 글자 수
    
    왜 자르나? → 임베딩 모델에 한 번에 너무 긴 텍스트를 넣으면
    의미가 희석되어 검색 정확도가 떨어집니다.
    """
    chunks = []
    for page in pages:
        text = page["text"]
        source = page["source"]
        page_num = page["page"]
        
        # chunk_size 단위로 자르되, overlap만큼 겹치게
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append({
                    "text": chunk.strip(),
                    "source": source,
                    "page": page_num
                })
            start += chunk_size - overlap  # 겹치는 부분만큼 뒤로
    
    print(f"  [OK] {len(chunks)} chunks created (size: {chunk_size}, overlap: {overlap})")
    return chunks


# ============================================
# [3단계] 임베딩 (Embedding) - 텍스트 → 숫자 벡터 변환
# ============================================
def get_embeddings(texts):
    """
    OpenAI 임베딩 API로 텍스트를 1536차원 벡터로 변환합니다.
    
    왜 벡터로 바꾸나? → "연차"와 "휴가"는 글자는 다르지만 의미가 비슷하므로
    벡터 공간에서 가까운 위치에 놓이게 됩니다. 이것이 '의미 검색'의 핵심!
    """
    client = OpenAI()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]


# ============================================
# [4단계] FAISS 인덱스 생성 및 저장
# ============================================
def build_index():
    """
    전체 파이프라인: PDF 읽기 → 청킹 → 임베딩 → FAISS 저장
    최초 1회만 실행하면 됩니다. (문서가 바뀌면 다시 실행)
    """
    print("=" * 50)
    print("[BUILD] Vector index building...")
    print("=" * 50)
    
    # 저장 폴더 생성
    os.makedirs(VECTOR_DIR, exist_ok=True)
    
    # 1. PDF 텍스트 추출
    print("\n[1/4] PDF 텍스트 추출 중...")
    pages = extract_text_from_pdfs()
    if not pages:
        print("[ERROR] No PDF files found in data/company_docs/")
        return False
    
    # 2. 청킹
    print("\n[2/4] 텍스트 청킹 중...")
    chunks = chunk_text(pages)
    
    # 3. 임베딩 (한 번에 최대 50개씩 배치 처리)
    print("\n[3/4] OpenAI 임베딩 변환 중...")
    all_embeddings = []
    batch_size = 50
    texts = [c["text"] for c in chunks]
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = get_embeddings(batch)
        all_embeddings.extend(embeddings)
        print(f"  [OK] {min(i + batch_size, len(texts))}/{len(texts)} chunks embedded")
    
    # 4. FAISS 인덱스 생성 및 저장
    print("\n[4/4] FAISS 벡터 인덱스 저장 중...")
    vectors = np.array(all_embeddings, dtype="float32")
    index = faiss.IndexFlatL2(EMBEDDING_DIM)  # L2 거리 기반 검색
    index.add(vectors)
    faiss.write_index(index, INDEX_PATH)
    
    # 청크 텍스트도 JSON으로 저장 (검색 결과에서 원문 참조용)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 50}")
    print(f"[DONE] Vector index created!")
    print(f"   - Chunks: {len(chunks)}")
    print(f"   - Dimension: {EMBEDDING_DIM}")
    print(f"   - Path: {VECTOR_DIR}")
    print(f"{'=' * 50}")
    return True


# ============================================
# [5단계] 벡터 검색 (챗봇에서 호출)
# ============================================
def search(query, top_k=3):
    """
    질문(query)과 가장 관련 있는 사내 규정 조각을 검색합니다.
    (FAISS 벡터 검색 + 단순 키워드 매칭(Hybrid))
    """
    if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        print("[WARNING] Vector index not found. Please run build_index() first.")
        return []
        
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    # 질문을 벡터로 변환
    query_embedding = get_embeddings([query])[0]
    query_vector = np.array([query_embedding], dtype="float32")
    
    # FAISS에서 여유 있게 상위 20개 검색
    distances, indices = index.search(query_vector, 20)
    
    results = []
    seen = set()
    
    # 불용어(Stop words) 제거
    stop_words = {"알려줘", "알려주세요", "대해", "대해서", "궁금해", "알고싶어", "정보", "어때", "무엇", "어떻게",
                  "해당", "되니", "되나요", "맞나요", "인가요", "입니까", "있나요", "없나요", "인지", "인가", "우리"}
    
    # 한국어 조사/어미 목록 (뒤에 붙는 것들)
    # 예: '근속승진에' → '근속승진' , '공가는' → '공가'
    KO_PARTICLES = ["에서", "에게", "이나", "에도", "이고", "이다", "부터", "까지", "로서",
                    "에", "이", "가", "을", "를", "은", "의", "로", "과", "와", "도", "만",
                    "고", "며", "는", "나", "서", "어", "해", "야", "냐", "니"]

    def strip_particles(word):
        """단어 끝의 조사/어미를 제거하여 어근(stem)을 반환합니다."""
        stems = {word}  # 원형도 포함
        for p in KO_PARTICLES:
            if word.endswith(p) and len(word) - len(p) >= 2:
                stems.add(word[:-len(p)])
        return stems

    # 띄어쓰기 기준 단어 추출(2글자 이상)
    raw_keywords = [kw for kw in query.split() if len(kw) >= 2]
    
    # 불용어와 '규정', '회사' 등 흔한 단어 제외한 핵심 키워드 추출
    base_keywords = [kw for kw in raw_keywords if kw not in stop_words and "규정" not in kw and "회사" not in kw]
    
    # 조사를 제거한 어근 변형도 추가 ('근속승진에' → '근속승진'도 검색)
    keywords = set()
    for kw in base_keywords:
        keywords.update(strip_particles(kw))
    
    # 이웃 단어 연결 형태도 추가 ('전직 시험' → '전직시험')
    for i in range(len(raw_keywords) - 1):
        merged = raw_keywords[i] + raw_keywords[i+1]
        if merged not in stop_words:
            keywords.update(strip_particles(merged))
    
    # 최소 2글자 이상인 것만 유효
    keywords = {kw for kw in keywords if len(kw) >= 2}
    
    # 만약 핵심 키워드가 없으면 원래 키워드 사용
    if not keywords:
        keywords = set(raw_keywords)
    

    # 1. FAISS 상위 20개 후보 추출 (의미적 유사도)
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks):
            chunk = chunks[idx]
            text = chunk["text"]
            dist = float(distances[0][i])
            
            # 키워드 매칭 개수 확인
            match_count = sum(1 for kw in keywords if kw in text)
            
            # [수정] 벡터 점수(dist)를 파격적으로 낮춰서(좋게 해서) 최상단으로 올림
            if match_count > 0:
                dist -= (1000.0 * match_count) # 훨씬 강력한 부스팅
            
            results.append({
                "source": chunk["source"],
                "page": chunk["page"],
                "text": text,
                "score": dist
            })
            seen.add(idx)

    # 2. [추가] FAISS 상위 20개에 없더라도, 키워드가 포함된 청크는 전수 조사해서 추가!
    # "근속승진" 같은 특정 단어가 벡터 검색에서 누락되는 경우를 방지합니다.
    for idx, chunk in enumerate(chunks):
        if idx in seen: continue
        
        text = chunk["text"]
        match_count = sum(1 for kw in keywords if kw in text)
        
        # 키워드 매칭이 있을 경우에만
        if match_count > 0:
            if text not in seen:
                results.append({
                    "text": text,
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "score": -200.0 - (100.0 * match_count) # 여러 키워드가 겹칠수록 최상단
                })
                seen.add(text)
                
    # 거리가 작은 순(가까운 순)으로 정렬 (음수일수록 위로)
    results.sort(key=lambda x: x["score"])
    
    return results[:top_k]


# 직접 실행하면 인덱스 빌드
if __name__ == "__main__":
    build_index()

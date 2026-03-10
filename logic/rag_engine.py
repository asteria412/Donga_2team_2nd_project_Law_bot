"""
============================================
logic/rag_engine.py
============================================
사내 규정 PDF → 청킹 → 임베딩 → FAISS 저장 / 챗봇 질의 시 관련 조각 검색

[모듈 구성]
- rag_engine_sam_config   : 경로, 임베딩 모델/차원
- rag_engine_sam_loader   : PDF 텍스트 추출
- rag_engine_sam_chunker  : 텍스트 청킹
- rag_engine_sam_embedder : OpenAI 임베딩
- rag_engine_sam_store    : 인덱스 빌드(오케스트레이션)
- rag_engine_sam_search   : 키워드 추출 등 검색 보조

[사용] 스트림릿 등에서 search는 이 파일에서 임포트합니다.
  from rag_engine_sam import search, build_index
"""
import os
import json
import faiss
import numpy as np
from dotenv import load_dotenv

load_dotenv()

from .rag import rag_engine_config as config
from .rag.rag_engine_store import build_index
from .rag.rag_engine_embedder import get_embeddings
from .rag.rag_engine_search import _extract_keywords


def search(query, top_k=3):
    """
    질문(query)과 가장 관련 있는 사내 규정 조각을 검색합니다.
    (FAISS 벡터 검색 + 키워드 매칭 하이브리드)
    스트림릿에서 from rag_engine_sam import search 로 사용합니다.
    """
    if not os.path.exists(config.INDEX_PATH) or not os.path.exists(config.CHUNKS_PATH):
        print("[WARNING] Vector index not found. Please run build_index() first.")
        return []

    index = faiss.read_index(config.INDEX_PATH)
    with open(config.CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    query_embedding = get_embeddings([query])[0]
    query_vector = np.array([query_embedding], dtype="float32")
    distances, indices = index.search(query_vector, 20)

    results = []
    seen = set()
    keywords = _extract_keywords(query)

    # 1. FAISS 상위 20개 후보 + 키워드 부스팅
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks):
            chunk = chunks[idx]
            text = chunk["text"]
            dist = float(distances[0][i])
            match_count = sum(1 for kw in keywords if kw in text)
            if match_count > 0:
                dist -= 1000.0 * match_count
            results.append({
                "source": chunk["source"],
                "page": chunk["page"],
                "text": text,
                "score": dist
            })
            seen.add(idx)

    # 2. 키워드 매칭 청크 전수 조사 추가
    for idx, chunk in enumerate(chunks):
        if idx in seen:
            continue
        text = chunk["text"]
        match_count = sum(1 for kw in keywords if kw in text)
        if match_count > 0:
            if text not in seen:
                results.append({
                    "text": text,
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "score": -200.0 - (100.0 * match_count)
                })
                seen.add(text)

    results.sort(key=lambda x: x["score"])
    return results[:top_k]


__all__ = ["build_index", "search"]

if __name__ == "__main__":
    build_index()

""" logic/rag_engine.py
[RAG 메인 컨트롤러] 무한개발공사 사내 규정 PDF 기반의 답변 생성을 위한 통합 진입점입니다.
벡터 검색(FAISS)과 키워드 매칭을 결합한 하이브리드 로직을 통해 '무한Law봇'의 검색 정확도를 제어하며,
규정 로드부터 인덱스 빌드까지 RAG 파이프라인 전 과정을 오케스트레이션합니다. 

[모듈 구성]
- config, loader, chunker, embedder, store, search 

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

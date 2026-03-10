"""
FAISS 인덱스 빌드 및 저장 (오케스트레이션).
"""
import os
import json
import faiss
import numpy as np

from . import rag_engine_config as config
from .rag_engine_loader import extract_text_from_pdfs
from .rag_engine_chunker import chunk_text
from .rag_engine_embedder import get_embeddings


def build_index():
    """
    전체 파이프라인: PDF 읽기 → 청킹 → 임베딩 → FAISS 저장
    최초 1회만 실행하면 됩니다. (문서가 바뀌면 다시 실행)
    """
    print("=" * 50)
    print("[BUILD] Vector index building...")
    print("=" * 50)

    os.makedirs(config.VECTOR_DIR, exist_ok=True)

    print("\n[1/4] PDF 텍스트 추출 중...")
    pages = extract_text_from_pdfs()
    if not pages:
        print("[ERROR] No PDF files found in data/company_docs/")
        return False

    print("\n[2/4] 텍스트 청킹 중...")
    chunks = chunk_text(pages)

    print("\n[3/4] OpenAI 임베딩 변환 중...")
    all_embeddings = []
    batch_size = 50
    texts = [c["text"] for c in chunks]
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = get_embeddings(batch)
        all_embeddings.extend(embeddings)
        print(f"  [OK] {min(i + batch_size, len(texts))}/{len(texts)} chunks embedded")

    print("\n[4/4] FAISS 벡터 인덱스 저장 중...")
    vectors = np.array(all_embeddings, dtype="float32")
    index = faiss.IndexFlatL2(config.EMBEDDING_DIM)
    index.add(vectors)
    faiss.write_index(index, config.INDEX_PATH)

    with open(config.CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 50}")
    print(f"[DONE] Vector index created!")
    print(f"   - Chunks: {len(chunks)}")
    print(f"   - Dimension: {config.EMBEDDING_DIM}")
    print(f"   - Path: {config.VECTOR_DIR}")
    print(f"{'=' * 50}")
    return True

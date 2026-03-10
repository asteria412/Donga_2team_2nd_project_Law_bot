"""
RAG 엔진 공통 설정: 경로, 임베딩 모델, 차원 등.
"""
import os

# app/test(backEnd_only) 기준 → 프로젝트 루트로 2단계 올라감
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR = os.path.join(BASE_DIR, "data", "company_docs")
VECTOR_DIR = os.path.join(BASE_DIR, "data", "vectorstore")
INDEX_PATH = os.path.join(VECTOR_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(VECTOR_DIR, "chunks.json")

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

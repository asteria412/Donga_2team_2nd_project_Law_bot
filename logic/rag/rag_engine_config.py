""" logic/rag/rag_engine_config.py
[RAG 엔진 공통 설정] 무한상사 'raw_bot' 프로젝트의 벡터 검색 및 문서 저장 경로를 관리하는 파일입니다.
'무한raw봇'이 참조할 사내 규정 PDF 경로, 임베딩 모델(OpenAI) 종류 및 벡터 차원 등 시스템의 핵심적인 물리적 환경 변수를 정의합니다. """

import os

# app/test(backEnd_only) 기준 → 프로젝트 루트로 2단계 올라감
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR = os.path.join(BASE_DIR, "data", "company_docs")
VECTOR_DIR = os.path.join(BASE_DIR, "data", "vectorstore")
INDEX_PATH = os.path.join(VECTOR_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(VECTOR_DIR, "chunks.json")

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

"""
임베딩 모듈 (OpenAI text-embedding-3-small).
"""
from openai import OpenAI

from . import rag_engine_config as config


def get_embeddings(texts):
    """OpenAI 임베딩 API로 텍스트를 벡터로 변환합니다."""
    client = OpenAI()
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]

""" logic/rag/rag_engine_embedder.py
[텍스트 임베딩 모듈] OpenAI API를 사용하여 추출된 텍스트를 벡터 데이터로 변환하는 파일입니다.
'무한raw봇'이 사내 규정의 의미를 파악하고 벡터 검색을 수행할 수 있도록 수치화된 데이터를 생성하며, 무한상사 'raw_bot' 프로젝트의 지능형 검색 성능을 결정하는 핵심 로직입니다. """

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

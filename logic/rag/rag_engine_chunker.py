""" logic/rag/rag_engine_chunker.py
[텍스트 청킹 모듈] 추출된 사내 규정 텍스트를 검색에 최적화된 크기로 분할하는 파일입니다.
'무한raw봇'이 방대한 규정 문서를 효율적으로 검색할 수 있도록 문맥 유지를 위한 중첩(Overlap)을 포함하여 의미 있는 조각(Chunk) 단위로 가공합니다. """

def chunk_text(pages, chunk_size=1000, overlap=200):
    """
    페이지별 텍스트를 chunk_size 글자 단위로 자릅니다.
    overlap: 앞뒤 문맥이 끊기지 않도록 겹치는 글자 수
    """
    chunks = []
    for page in pages:
        text = page["text"]
        source = page["source"]
        page_num = page["page"]

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
            start += chunk_size - overlap

    print(f"  [OK] {len(chunks)} chunks created (size: {chunk_size}, overlap: {overlap})")
    return chunks

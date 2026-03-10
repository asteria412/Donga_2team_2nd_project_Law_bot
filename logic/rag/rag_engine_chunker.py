"""
텍스트 청킹 모듈 (Chunking).
"""
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

""" logic/rag/rag_engine_loader.py
[PDF 데이터 로더] 무한상사의 사내 규정 문서(PDF)로부터 텍스트를 추출하는 파일입니다.
'raw_bot' 프로젝트의 지식 베이스 구축을 위해 지정된 경로의 PDF 파일을 페이지별로 읽어 들여 '무한raw봇'이 학습하고 검색할 수 있는 기초 데이터를 생성합니다. """

import os
import fitz

from . import rag_engine_config as config


def extract_text_from_pdfs():
    """data/company_docs/ 폴더의 모든 PDF에서 텍스트를 추출합니다."""
    all_text = []
    for filename in os.listdir(config.DOCS_DIR):
        if filename.endswith(".pdf"):
            filepath = os.path.join(config.DOCS_DIR, filename)
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

"""
PDF에서 텍스트 추출 모듈.
"""
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

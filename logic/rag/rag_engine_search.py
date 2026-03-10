""" logic/rag/rag_engine_search.py
[검색 보조 및 키워드 추출 모듈] '무한raw봇'의 하이브리드 검색 기능을 지원하기 위한 텍스트 처리 파일입니다.
사용자의 질문에서 불용어를 제거하고 한국어 조사를 분리하여 핵심 키워드를 추출하며, 이를 통해 무한상사 사내 규정 데이터 내에서 가장 관련성 높은 정보를 정확하게 찾아내도록 돕습니다. """

# 불용어
STOP_WORDS = {
    "알려줘", "알려주세요", "대해", "대해서", "궁금해", "알고싶어", "정보", "어때", "무엇", "어떻게",
    "해당", "되니", "되나요", "맞나요", "인가요", "입니까", "있나요", "없나요", "인지", "인가", "우리"
}

KO_PARTICLES = [
    "에서", "에게", "이나", "에도", "이고", "이다", "부터", "까지", "로서",
    "에", "이", "가", "을", "를", "은", "의", "로", "과", "와", "도", "만",
    "고", "며", "는", "나", "서", "어", "해", "야", "냐", "니"
]


def _strip_particles(word):
    """단어 끝의 조사/어미를 제거하여 어근(stem)을 반환합니다."""
    stems = {word}
    for p in KO_PARTICLES:
        if word.endswith(p) and len(word) - len(p) >= 2:
            stems.add(word[:-len(p)])
    return stems


def _extract_keywords(query):
    """쿼리에서 검색에 쓸 키워드 집합을 추출합니다. (rag_engine_sam.search에서 사용)"""
    raw_keywords = [kw for kw in query.split() if len(kw) >= 2]
    base_keywords = [
        kw for kw in raw_keywords
        if kw not in STOP_WORDS and "규정" not in kw and "회사" not in kw
    ]
    keywords = set()
    for kw in base_keywords:
        keywords.update(_strip_particles(kw))
    for i in range(len(raw_keywords) - 1):
        merged = raw_keywords[i] + raw_keywords[i + 1]
        if merged not in STOP_WORDS:
            keywords.update(_strip_particles(merged))
    keywords = {kw for kw in keywords if len(kw) >= 2}
    if not keywords:
        keywords = set(raw_keywords)
    return keywords

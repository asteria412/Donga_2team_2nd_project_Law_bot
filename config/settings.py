""" config/settings.py
[시스템 환경 설정] 프로젝트 전반에서 사용하는 외부 API 키와 법령 정보 서비스(law.go.kr) 접속을 위한 기본 설정 파일입니다.
보안이 필요한 키값을 로드하고, 데이터 수집을 위한 기본 URL 및 브라우저 헤더 정보를 중앙 관리하여 시스템의 통일성을 유지합니다. """

import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------
# API Key
# -----------------------
API_KEY = os.getenv("LAW_API_KEY")

# -----------------------
# Base URLs
# -----------------------
BASE_URL_LAW = "https://www.law.go.kr/DRF/lawSearch.do"
BASE_URL_SERVICE = "https://www.law.go.kr/DRF/lawService.do"

# -----------------------
# HTTP Headers
# -----------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/121.0.0.0 Safari/537.36"
    )
}

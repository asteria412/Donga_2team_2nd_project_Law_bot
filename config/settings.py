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

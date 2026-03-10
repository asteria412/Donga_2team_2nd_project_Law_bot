"""app\api\dependency.py
1. [설정 연결] .env에 숨겨둔 API 키나 DB 경로를 안전하게 읽어와 필요한 코드에 전달합니다.
2. [객체 재사용] 자주 쓰이는 기능을 매번 새로 만들지 않고 하나로 공유하도록 돕습니다.
3. [결합도 감소] 개별 기능 간의 의존성을 줄여 코드를 수정하거나 테스트할 때 다른 팀원의 작업에 영향을 주지 않게 합니다.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    openai_api_key: str = ""
    law_api_key: str = ""
    db_url: str = ""
    naver_client: str = ""
    naver_client_secret: str = ""


settings = Settings()


def get_settings():
    return settings
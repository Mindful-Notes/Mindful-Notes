# .env 관리
import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env 파일의 내용을 환경 변수로 불러옵니다.
load_dotenv()

"""시스템 환경 설정"""
class Settings(BaseSettings):
    SECRET_KEY: SecretStr
    ALGORITHMS: str = "HS256"
    DATABASE_URL: SecretStr
    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding='utf-8',
        extra='ignore', # .env에 클래스 변수 외에 다른게 있어도 무시
        case_sensitive=False
    )

settings = Settings()

"""db 연결 설정"""
TORTOISE_ORM = {
    "connections": {
        "default": settings.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}


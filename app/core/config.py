# .env 관리
import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

current_file_path = os.path.abspath(__file__)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
env_path = os.path.join(root_dir, ".env")

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


# 환경 변수에서 DATABASE_URL을 가져오고, 없으면 기본값을 사용하거나 에러를 냅니다.
database_url = os.getenv("DATABASE_URL")

TORTOISE_ORM = {
    "connections": {
        "default": database_url
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

# test
# if __name__ == "__main__":
#     try:
#         print(f"✅ 프로젝트 루트: {root_dir}")
#         print(f"✅ 설정파일 경로: {env_path}")
#         print(f"✅ 불러온 SECRET_KEY: {settings.SECRET_KEY}")
#     except Exception as e:
#         print(f"❌ 설정 로드 실패: {e}")
# .env 관리
# tortois
import os
from dotenv import load_dotenv

# .env 파일의 내용을 환경 변수로 불러옵니다.
load_dotenv()

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
# DB 세션 설정
from tortoise import Tortoise

from app.core.config import TORTOISE_ORM, settings


# DB를 연결하는 함수
async def init_db():
    # db_url을 str에서 SecretStr로 변경
    # await Tortoise.init(config=TORTOISE_ORM)

    await Tortoise.init(
        db_url=settings.DATABASE_URL.get_secret_value(),
        modules={"models": ["app.models"]},
    )

# DB 연결을 닫는 함수
async def close_db():
    await Tortoise.close_connections()
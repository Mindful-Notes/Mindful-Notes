# 앱 실행 및 라우터 통합
from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.diary.router import router as diary_router
from app.tags.router import router as tags_router
from app.core.config import settings

app = FastAPI()

app.include_router(auth_router)
app.include_router(diary_router)
app.include_router(tags_router)

from tortoise.contrib.fastapi import register_tortoise

register_tortoise(
    app,
    db_url=settings.DATABASE_URL.get_secret_value(),
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

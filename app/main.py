# 앱 실행 및 라우터 통합
from fastapi import FastAPI
from auth.router import router

app = FastAPI()
app.include_router(router)
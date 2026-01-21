# 앱 실행 및 라우터 통합
from fastapi import FastAPI
from app.core.database import engine, Base
from app.auth.router import router
import app.models

# 서버 시작 시 DB 테이블 생성
# Base.metadata.create_all은 models.py에 정의된 모든 테이블을 PostgreSQL DB에 생성함
Base.metadata.create_all(bind=engine)
app = FastAPI()

# 인증 관련 라우터 등록.
app.include_router(router)

@app.get("/")
def root():
    return {"message": "서버 정상 가동중."}
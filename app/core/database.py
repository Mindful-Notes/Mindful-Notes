# DB 세션 설정
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# .env 환경변수->config.py
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.get_secret_value()

# SQLAlchemy 엔진 생성
# pool_pre_ping: 연결이 살아있는지 체크 (DB가 꺼졌다가 켜졌을 때 에러 방지)
# pool_size: 동시에 유지할 연결 개수 (동시 접속자가 많을 때 유용)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델들이 상속받을 기본 클래스
Base = declarative_base()

# 종속성 주입을 위한 get_db함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # 사용이 끝나면 무조건 연결을 닫아 세션 반환
        db.close()
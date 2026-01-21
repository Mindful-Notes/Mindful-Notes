# fastapi
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.database import get_db
from pydantic import BaseModel

# 암호화
from jose import jwt, JWTError
from datetime import datetime, timedelta
from core.config import settings        # 환경변수 설정값 secret key 등
from core.database import get_db
from starlette import status
from auth.models import User



def create_access_token(user_id:int) -> str:
    payload = {
        "sub": str(user_id),            # JWT의 표준(sub)은 문자열
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# 헤더에서 Bearer 토큰 찾아 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Access Token ( JWT 형태)
ALGORITHM = "HS256"
SECRET_KEY = "MysteriousSecretKey"      # 환경변수로 !!
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 포괄적인 에러 정의
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 자격 증명이 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 서명확인, 페이로드 추출 / (토큰 해독)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if not user_id:         # None, [], 0, False 까지 포함.
            raise credentials_exception
            # DB에서 유저 조회
    except JWTError:
        # 서명이 틀렸거나 만료된 경우
        raise credentials_exception

    # DB에서 유저 확인
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise credentials_exception

    # 전부 통과하면 user 객체 반환
    return user


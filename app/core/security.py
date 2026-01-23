# -*- coding: utf-8 -*-
# fastapi
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.security import OAuth2PasswordBearer
# from pydantic import BaseModel

import sys
from pathlib import Path
root_path = str(Path(__file__).parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

# 암호화
from ..models import TOKEN_BLACKLIST, USERS
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.core.config import settings        # 환경변수 설정값 secret key 등
from starlette import status



def create_access_token(user_id:int) -> str:
    payload = {
        "sub": str(user_id),            # JWT의 표준(sub)은 문자열
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)

# 헤더에서 Bearer 토큰 찾아 추출
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
http_schema = HTTPBearer()

# Access Token ( JWT 형태)
ALGORITHM = "HS256"
SECRET_KEY = settings.SECRET_KEY.get_secret_value()
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# async def get_current_user(token: str = Depends(oauth2_scheme)):   # 포괄적인 에러 정의
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="인증 자격 증명이 유효하지 않습니다.",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     # 블랙리스트 확인 (보안 강화)
#     blacklisted = await TOKEN_BLACKLIST.filter(token=token).exists()
#     if blacklisted:
#         raise credentials_exception
#     try:
#         # 서명확인, 페이로드 추출 / (토큰 해독)
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: str = payload.get("sub")
#
#         if not user_id:         # None, [], 0, False 까지 포함.
#             raise credentials_exception
#             # DB에서 유저 조회
#     except JWTError:
#         # 서명이 틀렸거나 만료된 경우
#         raise credentials_exception
#
#     # DB에서 유저 확인
#     user = await USERS.filter(user_id=int(user_id)).first()
#
#     if user is None:
#         raise credentials_exception
#
#     # 전부 통과하면 user 객체 반환
#     return user

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(http_schema)):
    token = auth.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 자격 증명이 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    blacklisted = await TOKEN_BLACKLIST.filter(token=token).exists()
    if blacklisted:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if not user_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await USERS.filter(user_id=int(user_id)).first()

    if user is None:
        raise credentials_exception

    return user

# 비밀번호 해싱을 위한 설정 (bcrypt 알고리즘 사용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 해시 함수
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Hash 전 비밀번호화 Hash된 비밀번호 비교
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


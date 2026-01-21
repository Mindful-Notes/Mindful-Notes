from pydoc import describe

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from jose import jwt
from core.config import Settings
from core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    oauth2_scheme
)
from models import User, TokenBlacklist
from auth.schemas import UserCreate, Token, UserOut

router = APIRouter(
    prefix="/auth",
    tags=["인증"],
)

# 회원가입
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 이메일입니다.")

    new_user = User(
        email=user.email,
        hashed_password = get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 로그인, 토큰발급)
@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm 형태는 JSON 아니라 Form, Depends(생략가능)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail = "로그인 정보가 정확하지 않습니다.")

    access_token = create_access_token(user_id = user.user_id, fresh = True)
    return {"access_token": access_token, "token_type": "bearer"}

# 로그아웃, 토큰 블랙리스트 등록
@router.get("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # 클라이언트가 보낸 토큰을 SECRET_KEY로 복호화
        payload = jwt.decode(
            token,
            Settings.SECRET_KEY
            , algorithms= [Settings.ALGORITHMS]
        )

        token_exp = payload.get("exp")
        if token_exp is None:
            raise HTTPException(status_code=400, detail="유효하지 않은 토큰")
        # payload에서 exp(숫자) -> 파이썬 datetime 객체로 바꿈.
        exp_datetime = datetime.fromtimestamp(token_exp)

        # 블랙리스트 테이블에 등록
        blacklisted_token = TokenBlacklist(
            token = token,
            expires_at = exp_datetime
        )
        db.add(blacklisted_token)
        db.commit()

    except jwt.ExpiredSignatureError:
        return {"message": "이미 만료된 토큰입니다."}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "성공적으로 로그아웃되었습니다."}

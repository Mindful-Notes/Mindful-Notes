from pydantic import BaseModel, EmailStr
from typing import Optional

# 회원가입 / 로그인 시 받는 데이터 (Input)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 로그인 성공 시 반환하는 토큰 형식 (Output)
class Token(BaseModel):
    access_token: str
    token_type: str

# API 응답으로 유저 정보 보여줄 때 (Output)
class UserOut(BaseModel):
    user_id: int
    email: EmailStr

    class Config:
        from_attributes = True          # SQLAlchemy 객체를 자동으로 읽어오게 함.
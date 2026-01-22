# .env 관리
# tortois
import os
from pathlib import Path
from pydantic import SecretStr, BaseModel, Field, EmailStr
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

BASE_DIR = Path(__file__).parent.parent.parent
env_path = BASE_DIR / ".env"

"""시스템 환경 설정"""
class Settings(BaseSettings):
    SECRET_KEY: SecretStr
    ALGORITHMS: str = "HS256"
    DATABASE_URL: SecretStr
    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding='utf-8',
        extra='ignore', # .env에 클래스 변수 외에 다른게 있어도 무시
        case_sensitive=False
    )

settings = Settings()

"""db 연결 설정"""
TORTOISE_ORM = {
    "connections": {
        "default": settings.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

"""pydantic 모델"""
class PostStatus(str, Enum):
    PUBLIC = "public"
    DELETED = "deleted"

class StatusUpdate(BaseModel):
    is_active: bool


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
    email: EmailStr = Field(validation_alias="user_email")

    class Config:
        from_attributes = True          # SQLAlchemy 객체를 자동으로 읽어오게 함.

"""유저 스키마"""
class UserBase(BaseModel):
    # 공통요소
    user_email: EmailStr

class UserResponse(UserBase):
    # 결과출력
    user_id: int
    cdate: datetime

    class Config:
        from_attributes = True

"""명언 스키마 - 스크래핑"""
class QuoteCreate(BaseModel):
    # DB 입구
    contents: str = Field(..., min_length=1, max_length=500)
    author: Optional[str] = Field(None, max_length=100)

class QuoteResponse(QuoteCreate):
    # DB 출구
    quote_id: int
    is_active: bool
    cdate: datetime

    class Config:
        # ORM 객체 -> json 객체
        from_attributes = True

"""오늘의질문 스키마 - 스크래핑"""
class QuestionCreate(BaseModel):
    contents: str = Field(..., min_length=1, max_length=500)

class QuestionResponse(QuestionCreate):
    question_id: int
    is_active: bool
    cdate: datetime

    class Config:
        # ORM 객체 -> json 객체
        from_attributes = True

"""일기 & 태그 스키마"""
class TagBase(BaseModel):
    name: str = Field(..., max_length=50)

class TagResponse(TagBase):
    tag_id: int
    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    contents: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list, description="태그 이름 리스트")
    attached: str | None = Field(None, max_length=255, description="첨부파일 URL/경로")

class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    contents: str | None = Field(None, min_length=1)
    tags: list[str] | None = Field(None, description="보내면 태그 교체, 안 보내면 유지")
    attached: str | None = Field(None, max_length=255, description="첨부파일 URL/경로")


class PostResponse(BaseModel):
    post_id: int
    user_id: int
    title: str
    contents: str
    attached: Optional[str] = None
    status: PostStatus
    cdate: datetime
    # ManyToMany 관계인 태그 목록을 포함
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True

"""북마크 스키마"""
class BookmarkCreate(BaseModel):
    quote_id: int

class BookmarkResponse(BaseModel):
    bookmark_id: int
    user_id: int
    quote_id: int
    cdate: datetime

    class Config:
        from_attributes = True
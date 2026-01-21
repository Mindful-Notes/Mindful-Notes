from pydantic_settings import BaseSettings, SettingsConfigDict

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

"""시스템 환경 설정"""
class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHMS: str = "HS256"
    DATABASE_URL: str
    model_config = SettingsConfigDict(env_file=".env")

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

"""유저 스키마"""
class UserBase(BaseModel):
    # 공통요소
    user_email: EmailStr

class UserCreate(UserBase):
    # 회원가입
    password: str = Field(..., min_length=8)

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
    contents: str
    attached: Optional[str] = None
    tags: List[str] = [] # 생성 시 태그 이름 리스트를 받음

class PostResponse(BaseModel):
    post_id: int
    user_id: int
    title: str
    contents: str
    attached: Optional[str]
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
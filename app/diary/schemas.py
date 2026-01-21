# "일기 입력/출력 규격(Pydantic)"
# 역할: API 요청/응답 데이터 규격(검증) 담당

from datetime import datetime
from pydantic import BaseModel, Field


class DiaryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    contents: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list, description="태그 이름 리스트")
    attached: str | None = Field(None, max_length=255, description="첨부파일 URL/경로")


class DiaryUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    contents: str | None = Field(None, min_length=1)

    # 보내면 태그 교체 / 안 보내면 유지
    tags: list[str] | None = Field(None, description="보내면 태그 교체, 안 보내면 유지")

    attached: str | None = Field(None, max_length=255, description="첨부파일 URL/경로")

class DiaryOut(BaseModel):
    post_id: int
    user_id: int
    title: str
    contents: str
    tags: list[str]
    attached: str | None
    cdate: datetime

## 일단 태그/첨부파일 안 받게 최소화
## 응답도 핵심만 보내도록 단순화
import random
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import (
    BookmarkCreate,
    BookmarkResponse,
    QuestionResponse,
    QuoteResponse,
    StatusUpdate
)
from app.core.security import get_current_user
from app.models import BOOKMARKS, QUOTES, REFLECTION_QUESTIONS

router = APIRouter()

@router.get("/quotes", response_model=List[QuoteResponse])
async def get_active_quotes():
    """활성화된 모든 명언"""
    return await QuoteResponse.from_queryset(QUOTES.filter(is_active=True))

@router.get("/quotes/random", response_model=QuoteResponse)
async def get_random_quote():
    """랜덤명언 뽑기"""
    count = await QUOTES.filter(is_active=True).count()
    if count == 0:
        raise HTTPException(status_code=404, detail="명언이 없습니다.")

    random_offset = random.randint(0, count - 1)
    quote = await QUOTES.filter(is_active=True).offset(random_offset).first()
    return quote

@router.patch("/quotes/{quote_id}/status", response_model=QuoteResponse)
async def update_quote_status(quote_id: int, status: StatusUpdate):
    """명언 활성화/비활성화 전환"""
    quote = await QUOTES.filter(id=quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="명언을 찾을 수 없습니다.")

    quote.is_active = status.is_active
    await quote.save()
    return quote


@router.get("/questions", response_model=List[QuestionResponse])
async def get_active_questions():
    """활성화된 오늘의 질문 리스트"""
    return await QuestionResponse.from_queryset(
        REFLECTION_QUESTIONS.filter(is_active=True)
    )

@router.get("/questions/random", response_model=QuestionResponse)
async def get_random_question():
    """오늘의 질문 랜덤 뽑기"""
    count = await REFLECTION_QUESTIONS.filter(is_active=True).count()

    if count == 0:
        raise HTTPException(status_code=404, detail="등록된 질문이 없습니다.")

    random_offset = random.randint(0, count - 1)

    question = (
        await REFLECTION_QUESTIONS.filter(is_active=True).offset(random_offset).first()
    )

    return question

@router.patch("/questions/{question_id}/status", response_model=QuestionResponse)
async def update_question_status(question_id: int, status: StatusUpdate):
    """오늘의 질문 활성화/비활성화 전환"""
    question = await REFLECTION_QUESTIONS.filter(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")

    question.is_active = status.is_active
    await question.save()
    return question


@router.post("/bookmarks", response_model=BookmarkResponse)
async def add_bookmark(
    bookmark_in: BookmarkCreate,
    current_user=Depends(get_current_user),
):
    """북마크 추가"""
    exists = await BOOKMARKS.filter(
        user_id=current_user.user_id, quote_id=bookmark_in.quote_id
    ).exists()

    if exists:
        raise HTTPException(status_code=400, detail="이미 북마크했습니다.")

    new_bookmark = await BOOKMARKS.create(
        user_id=current_user.user_id, quote_id=bookmark_in.quote_id
    )
    return new_bookmark


@router.delete("/bookmarks/{quote_id}")
async def remove_bookmark(quote_id: int, current_user=Depends(get_current_user)):
    """북마크를 삭제"""
    deleted_count = await BOOKMARKS.filter(user_id=current_user.user_id, quote_id=quote_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다.")
    return {"message": "북마크가 삭제되었습니다."}

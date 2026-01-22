from fastapi import APIRouter, Depends, Query, status
from app.core.config import PostCreate, PostResponse, PostUpdate
from app.diary import service
from app.diary.deps import get_me
from app.models import TAGS, POST_TAGS

router = APIRouter(prefix="/diaries", tags=["Diary"])

async def to_out(post) -> PostResponse:
    """Tortoise M2M 객체를 Pydantic Response 모델로 변환 (중간 테이블 직접 조회 방식)"""

    rels = await POST_TAGS.filter(post_id=post.post_id).all()
    tag_ids = [r.tag_id for r in rels]

    tag_names = []
    if tag_ids:
        tags = await TAGS.filter(tag_id__in=tag_ids).all()
        tag_names = [t.name for t in tags]

    # print(f"--- DEBUG: POST_ID {post.post_id} -> RELS_FOUND: {len(rels)} -> TAGS: {tag_names} ---")

    return PostResponse(
        post_id=post.post_id,
        user_id=post.user_id,
        title=post.title,
        contents=post.contents,
        tags=tag_names,
        attached=post.attached,
        status=post.status,
        cdate=post.cdate,
    )
@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_diary_api(payload: PostCreate, me=Depends(get_me)):
    post = await service.create_diary(me.user_id, payload)
    return await to_out(post)

@router.get("", response_model=list[PostResponse])
async def list_diaries_api(
    q: str | None = Query(None),
    tag: str | None = Query(None),
    sort: str = Query("latest", pattern="^(latest|oldest)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    me=Depends(get_me),
):
    posts = await service.list_diaries(me.user_id, q, tag, sort, skip, limit)
    return [await to_out(p) for p in posts]

@router.get("/{post_id}", response_model=PostResponse)
async def get_diary_api(post_id: int, me=Depends(get_me)):
    post = await service.get_diary(post_id, me.user_id)
    return await to_out(post)

@router.patch("/{post_id}", response_model=PostResponse)
async def update_diary_api(post_id: int, payload: PostUpdate, me=Depends(get_me)):
    post = await service.update_diary(post_id, me.user_id, payload)
    return await to_out(post)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diary_api(post_id: int, me=Depends(get_me)):
    await service.delete_diary(post_id, me.user_id)
    return None

@router.post("/{post_id}/restore", response_model=PostResponse)
async def restore_diary_api(post_id: int, me=Depends(get_me)):
    post = await service.restore_diary(post_id, me.user_id)
    return await to_out(post)
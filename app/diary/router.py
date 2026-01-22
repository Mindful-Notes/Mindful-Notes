# URL 접수처 (Router)

from fastapi import APIRouter, Depends, Query, status

from app.core.config import PostCreate, PostResponse, PostUpdate
from app.diary import service
from app.diary.deps import get_me

router = APIRouter(prefix="/diaries", tags=["Diary"])


async def to_out(post) -> PostResponse:
    """
    Tortoise ManyToMany(tags) 대응:
    - tags가 M2M 매니저면 await post.tags.all() 필요
    - tags가 이미 리스트면 그대로 사용
    """
    tag_names: list[str] = []

    if hasattr(post, "tags"):
        try:
            tags = await post.tags.all()
            tag_names = [t.name for t in tags]
        except TypeError:
            tag_names = [t.name for t in post.tags]

    return PostResponse(
        post_id=getattr(post, "post_id", None) or getattr(post, "id", None),
        user_id=post.user_id,
        title=post.title,
        contents=post.contents,
        tags=tag_names,
        attached=getattr(post, "attached", None),
        status=getattr(post, "status", "public"),
        cdate=post.cdate,
    )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_diary_api(payload: PostCreate, me=Depends(get_me)):
    post = await service.create_diary(
        me.user_id,
        payload.title,
        payload.contents,
        payload.tags,
        payload.attached,
    )
    return await to_out(post)


@router.get("", response_model=list[PostResponse])
async def list_diaries_api(
    q: str | None = Query(None, description="제목/내용 검색(구현 방식은 service에서)"),
    tag: str | None = Query(None, description="태그 필터"),
    sort: str = Query("latest", pattern="^(latest|oldest)$", description="latest | oldest"),
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
    post = await service.update_diary(
        post_id,
        me.user_id,
        payload.title,
        payload.contents,
        payload.tags,
        payload.attached,
    )
    return await to_out(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diary_api(post_id: int, me=Depends(get_me)):
    await service.delete_diary(post_id, me.user_id)
    return None


@router.post("/{post_id}/restore", response_model=PostResponse)
async def restore_diary_api(post_id: int, me=Depends(get_me)):
    post = await service.restore_diary(post_id, me.user_id)
    return await to_out(post)



## to_out()로 응답 형태 강제 통일 -> API응답 안정성
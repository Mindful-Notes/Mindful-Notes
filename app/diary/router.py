# "URL 접수처"

from fastapi import APIRouter, Depends, Query
from app.diary.schemas import DiaryCreate, DiaryUpdate, DiaryOut
from app.diary import service
from app.diary.deps import get_me

router = APIRouter(prefix="/diaries", tags=["Diary"])


def to_out(post) -> DiaryOut:
    tag_names = [t.name for t in post.tags] if hasattr(post, "tags") else []

    return DiaryOut(
        post_id=post.post_id,
        user_id=post.user_id,
        title=post.title,
        contents=post.contents,
        tags=tag_names,
        attached=post.attached,
        cdate=post.cdate,
    )



@router.post("", response_model=DiaryOut)
async def create_diary_api(payload: DiaryCreate, me=Depends(get_me)):
    post = await service.create_diary(
        me.user_id,
        payload.title,
        payload.contents,
        payload.tags,
        payload.attached,
    )
    return to_out(post)


@router.patch("/{post_id}", response_model=DiaryOut)
async def update_diary_api(post_id: int, payload: DiaryUpdate, me=Depends(get_me)):
    post = await service.update_diary(
        post_id,
        me.user_id,
        payload.title,
        payload.contents,
        payload.tags,
        payload.attached,
    )

    # ✅ 내 글만 조회 가능하도록 할건지??
    if post.user_id_id != me.user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="본인 글만 조회할 수 있습니다.")

    return to_out(post)


@router.get("", response_model=list[DiaryOut])
async def list_diaries_api(
    q: str | None = Query(None, description="제목 검색"),
    tag: str | None = Query(None, description="태그 필터"),
    sort: str = Query("latest", description="latest | oldest"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    me=Depends(get_me),
):
    posts = await service.list_diaries(me.user_id, q, tag, sort, skip, limit)
    return [to_out(p) for p in posts]


@router.patch("/{post_id}", response_model=DiaryOut)
async def update_diary_api(post_id: int, payload: DiaryUpdate, me=Depends(get_me)):
    post = await service.update_diary(post_id, me.user_id, payload.title, payload.contents)
    return to_out(post)


@router.delete("/{post_id}")
async def delete_diary_api(post_id: int, me=Depends(get_me)):
    return await service.delete_diary(post_id, me.user_id)

# 복구 API
@router.post("/{post_id}/restore")
async def restore_diary_api(post_id: int, me=Depends(get_me)):
    return await service.restore_diary(post_id, me.user_id)


## to_out()로 응답 형태 강제 통일 -> API응답 안정성
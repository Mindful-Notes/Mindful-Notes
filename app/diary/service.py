from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from tortoise import transactions

from app.core.config import PostCreate, PostUpdate
from app.models import POSTS, TAGS, POST_TAGS, PostStatus

# 삭제 보관 기간 = 3일
RESTORE_WINDOW_DAYS = 3

async def create_diary(user_id: int, payload: PostCreate):
    """일기 생성 및 태그 연결 (트랜잭션 보장)"""
    async with transactions.in_transaction():
        post = await POSTS.create(
            user_id=user_id,
            **payload.model_dump(exclude={"tags"}),
            status=PostStatus.PUBLIC,
        )

        if payload.tags:
            tag_objs = await get_or_create_tags(payload.tags)
            await post.tags.add(*tag_objs)

    return await POSTS.filter(post_id=post.post_id).prefetch_related("tags").first()


async def get_diary(post_id: int, user_id: int):
    """특정 일기 상세 조회"""
    post = await POSTS.filter(
        post_id=post_id,
        status=PostStatus.PUBLIC,
    ).prefetch_related("tags").first()

    if not post:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="본인 글만 조회할 수 있습니다.")

    return post


async def list_diaries(
    user_id: int,
    q: str | None,
    tag: str | None,
    sort: str,
    skip: int,
    limit: int,
):
    """일기 목록 조회 (검색 및 정렬)"""
    qs = POSTS.filter(
        user_id=user_id,
        status=PostStatus.PUBLIC,
    )

    if q:
        qs = qs.filter(title__icontains=q)

    if tag:
        qs = qs.filter(tags__name=tag)

    # 정렬 처리 (모델의 cdate 필드 기준)
    if sort == "latest":
        qs = qs.order_by("-cdate")
    elif sort == "oldest":
        qs = qs.order_by("cdate")
    else:
        raise HTTPException(status_code=400, detail="sort는 latest/oldest 중 하나여야 합니다.")

    return await qs.prefetch_related("tags").offset(skip).limit(limit).all()


async def update_diary(post_id: int, user_id: int, payload: PostUpdate):
    post = await POSTS.filter(
        post_id=post_id, user=user_id, status=PostStatus.PUBLIC
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    async with transactions.in_transaction():
        update_data = payload.model_dump(exclude_unset=True, exclude={"tags"})
        if update_data:
            for key, value in update_data.items():
                setattr(post, key, value)
            await post.save()

        if payload.tags is not None:
            await POST_TAGS.filter(post_id=post_id).delete()

            if payload.tags:
                tag_objs = await get_or_create_tags(payload.tags)

                new_rels = [
                    POST_TAGS(post_id=post_id, tag_id=t.tag_id) for t in tag_objs
                ]
                await POST_TAGS.bulk_create(new_rels)

    return await POSTS.filter(post_id=post_id).prefetch_related("tags").first()


async def get_or_create_tags(tag_names: list[str]):
    """태그 문자열 리스트를 받아 TAGS 객체 리스트로 변환"""
    cleaned = list(dict.fromkeys([n.strip() for n in tag_names if n.strip()]))

    tag_objs = []
    for name in cleaned:
        tag, _ = await TAGS.get_or_create(name=name)
        tag_objs.append(tag)

    return tag_objs


async def delete_diary(post_id: int, user_id: int):
    """일기 삭제 (Soft Delete)"""
    post = await POSTS.filter(
        post_id=post_id,
        user_id=user_id,
        status=PostStatus.PUBLIC,
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    post.status = PostStatus.DELETED
    post.deleted_date = datetime.now(timezone.utc)
    await post.save()

    return {"message": "삭제 완료 (soft delete)"}


async def restore_diary(post_id: int, user_id: int):
    """삭제된 일기 복구 (3일 이내만 가능)"""
    post = await POSTS.filter(
        post_id=post_id,
        user_id=user_id,
        status=PostStatus.DELETED,
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="복구할 삭제 글이 없습니다.")

    # 복구 가능 기간 체크
    deadline = datetime.now(timezone.utc) - timedelta(days=RESTORE_WINDOW_DAYS)

    if post.deleted_date and post.deleted_date <= deadline:
        raise HTTPException(status_code=400, detail="삭제 후 3일이 지나 복구할 수 없습니다.")

    post.status = PostStatus.PUBLIC
    post.deleted_date = None
    await post.save()

    return await POSTS.filter(post_id=post_id).prefetch_related("tags").first()
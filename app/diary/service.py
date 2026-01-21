# "실제 로직(저장/조회/수정/삭제)"
# 검색/정렬 등 복잡한 로직

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from app.models import POSTS, TAGS, PostStatus  # 너희 Tortoise 모델 별칭/경로 유지

# 삭제 보관 기간 = 3일
RESTORE_WINDOW_DAYS = 3


async def create_diary(
    user_id: int,
    title: str,
    contents: str,
    tags: list[str],
    attached: str | None,
):
    post = await POSTS.create(
        user_id=user_id,
        title=title,
        contents=contents,
        attached=attached,
        status=PostStatus.PUBLIC,
    )

    if tags:
        await set_post_tags(post, tags)

    # tags 포함해서 반환위해 prefetch로 다시 가져오기
    return await POSTS.filter(post_id=post.post_id).prefetch_related("tags").first()


async def get_diary(post_id: int):
    post = await POSTS.filter(
        post_id=post_id,
        status=PostStatus.PUBLIC,  # 공개 글만 조회
    ).prefetch_related("tags").first()

    if not post:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")
    return post


async def list_diaries(
    user_id: int,
    q: str | None,
    tag: str | None,
    sort: str,
    skip: int,
    limit: int,
):
    qs = POSTS.filter(
        user_id=user_id,
        status=PostStatus.PUBLIC,
    )

    # 제목/내용 검색을 원하면 title__contains OR contents__contains로 확장 가능
    if q:
        qs = qs.filter(title__contains=q)

    # 태그 필터링 (ManyToMany)
    if tag:
        qs = qs.filter(tags__name=tag)

    if sort == "latest":
        qs = qs.order_by("-cdate")
    elif sort == "oldest":
        qs = qs.order_by("cdate")
    else:
        raise HTTPException(status_code=400, detail="sort는 latest/oldest 중 하나여야 합니다.")

    return await qs.prefetch_related("tags").offset(skip).limit(limit).all()


async def update_diary(
    post_id: int,
    user_id: int,
    title: str | None,
    contents: str | None,
    tags: list[str] | None,
    attached: str | None,
):
    post = await POSTS.filter(
        post_id=post_id,
        status=PostStatus.PUBLIC,
    ).prefetch_related("tags").first()

    if not post:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="본인 글만 수정할 수 있습니다.")

    if title is not None:
        post.title = title
    if contents is not None:
        post.contents = contents

    # attached를 None으로 "삭제"까지 지원하려면,
    # 라우터에서 payload에 attached가 포함됐는지 여부를 함께 넘겨야 함.
    # 지금은 "None이면 유지, 문자열이면 수정" 규칙으로 간단 처리.
    if attached is not None:
        post.attached = attached

    await post.save()

    # tags가 None이면 유지 / 리스트면 교체
    if tags is not None:
        await set_post_tags(post, tags)

    return await POSTS.filter(post_id=post_id).prefetch_related("tags").first()


async def get_or_create_tags(tag_names: list[str]):
    cleaned: list[str] = []
    for name in tag_names:
        n = name.strip()
        if n:
            cleaned.append(n)

    # 중복 제거(순서 유지)
    cleaned = list(dict.fromkeys(cleaned))

    tag_objs = []
    for name in cleaned:
        tag = await TAGS.filter(name=name).first()
        if not tag:
            tag = await TAGS.create(name=name)
        tag_objs.append(tag)

    return tag_objs


async def set_post_tags(post, tag_names: list[str]):
    tag_objs = await get_or_create_tags(tag_names)

    await post.tags.clear()
    if tag_objs:
        await post.tags.add(*tag_objs)


async def delete_diary(post_id: int, user_id: int):
    post = await POSTS.filter(
        post_id=post_id,
        status=PostStatus.PUBLIC,
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인 글만 삭제할 수 있습니다.",
        )

    post.status = PostStatus.DELETED
    post.deleted_date = datetime.now(timezone.utc)
    await post.save()


    return {"message": "삭제 완료 (soft delete)"}


async def restore_diary(post_id: int, user_id: int):
    post = await POSTS.filter(
        post_id=post_id,
        status=PostStatus.DELETED,
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="복구할 삭제 글이 없습니다.")

    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인 글만 복구할 수 있습니다.",
        )

    if not post.deleted_date:
        raise HTTPException(status_code=400, detail="deleted_date가 없어 복구할 수 없습니다.")

    deadline = datetime.now(timezone.utc) - timedelta(days=RESTORE_WINDOW_DAYS)

    if post.deleted_date <= deadline:
        raise HTTPException(status_code=400, detail="삭제 후 3일이 지나 복구할 수 없습니다.")

    post.status = PostStatus.PUBLIC
    post.deleted_date = None
    await post.save()

    return await POSTS.filter(post_id=post_id).prefetch_related("tags").first()



## PUBLIC 필터 넣기완료
## 내 글만 수정/삭제 권한 체크

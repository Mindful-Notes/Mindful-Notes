# 삭제된 지 3일 지난 글들 DB에서 진짜 삭제하는 스크립트

import asyncio
from datetime import datetime, timedelta, timezone

from tortoise import Tortoise

from app.core.config import TORTOISE_ORM
from app.models import POSTS, PostStatus

PURGE_AFTER_DAYS = 3


async def purge():
    await Tortoise.init(config=TORTOISE_ORM)

    cutoff = datetime.now(timezone.utc) - timedelta(days=PURGE_AFTER_DAYS)

    # 삭제 상태 + 삭제 시점이 cutoff보다 이전인 것들 = 물리 삭제 대상
    targets = await POSTS.filter(
        status=PostStatus.DELETED,
        deleted_date__lt=cutoff
    )

    count = len(targets)

    for post in targets:
        await post.delete()

    await Tortoise.close_connections()
    print(f"[PURGE] deleted posts removed: {count}")


if __name__ == "__main__":
    asyncio.run(purge())

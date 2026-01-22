from fastapi import APIRouter

from app.models import TAGS

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("")
async def list_tags():
    tags = await TAGS.all().order_by("name")
    return [{"tag_id": t.tag_id, "name": t.name} for t in tags]

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, timezone
from app.models import TOKEN_BLACKLIST, POSTS, PostStatus

async def delete_expired_tokens():
    """
    Deletes expired tokens from the token blacklist.
    """
    now = datetime.now(timezone.utc)
    expired_tokens = await TOKEN_BLACKLIST.filter(expires_at__lt=now)
    for token in expired_tokens:
        await token.delete()
    print(f"[{now}] Deleted {len(expired_tokens)} expired tokens.")

async def delete_old_posts():
    """
    Deletes posts that were marked as deleted more than 3 days ago.
    """
    now = datetime.now(timezone.utc)
    three_days_ago = now - timedelta(days=3)
    old_posts = await POSTS.filter(
        status=PostStatus.DELETED, deleted_date__lt=three_days_ago
    )
    for post in old_posts:
        await post.delete()
    print(f"[{now}] Deleted {len(old_posts)} old posts.")

# def setup_scheduler():
#     """
#     Sets up and starts the scheduler.
#     """
#     scheduler = AsyncIOScheduler(timezone="UTC")
#     scheduler.add_job(delete_expired_tokens, CronTrigger(hour=0))  # Runs daily at midnight
#     scheduler.add_job(delete_old_posts, CronTrigger(hour=1))  # Runs daily at 1 AM
#     scheduler.start()
#     print("Scheduler started.")
#     return scheduler
def setup_scheduler():
    """
    Sets up and starts the scheduler.
    """
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(delete_expired_tokens, CronTrigger(hour=6))  # Runs daily at midnight
    scheduler.add_job(delete_old_posts, CronTrigger(hour=1))  # Runs daily at 1 AM
    scheduler.start()
    print("Scheduler started.")
    return scheduler

import asyncio
from tortoise import Tortoise, run_async
from app.models import POSTS, TAGS, PostStatus, USERS

async def init():
    # Use in-memory SQLite for reproduction
    await Tortoise.init(
        db_url='sqlite://:memory:',
        modules={'models': ['app.models']}
    )
    await Tortoise.generate_schemas()

async def run():
    await init()
    
    # Create dummy user
    user = await USERS.create(
        user_email="test@example.com",
        hashed_pass="hashed_secret"
    )
    
    # Create post
    post = await POSTS.create(
        user=user,
        title="Test Diary",
        contents="Testing tags",
        status=PostStatus.PUBLIC
    )
    
    # Create tag
    tag = await TAGS.create(name="happy")
    
    print("Attempting to add tag to post...")
    try:
        # This is where it should fail if column names are mismatched
        await post.tags.add(tag)
        print("Successfully added tag!")
    except Exception as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    run_async(run())

from enum import Enum
from tortoise import fields, models

class PostStatus(str, Enum):
    PUBLIC = "public"
    DELETED = "deleted"

class USERS(models.Model):
    user_id = fields.IntField(pk=True)
    user_email = fields.CharField(max_length=255, unique=True)
    hashed_pass = fields.CharField(max_length=255)
    cdate = fields.DatetimeField(auto_now_add=True)

class POSTS(models.Model):
    post_id = fields.IntField(pk=True)
    # 변수명을 user로 하면 사용하기 더 편합니다 (post.user.user_email 가능)
    user = fields.ForeignKeyField(
        "models.USERS", related_name="posts", db_constraint=True, source_field="user_id"
    )
    title = fields.CharField(max_length=255)
    contents = fields.TextField()
    attached = fields.CharField(max_length=255, null=True)
    status = fields.CharEnumField(PostStatus, default=PostStatus.PUBLIC, index=True)
    deleted_date = fields.DatetimeField(null=True)
    cdate = fields.DatetimeField(auto_now_add=True)

    # models. 을 붙여주는 것이 더 안전합니다.
    tags = fields.ManyToManyField(
        "models.TAGS", related_name="posts", through="POST_TAGS"
    )

class TAGS(models.Model):
    tag_id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)

class POST_TAGS(models.Model):
    id = fields.IntField(pk=True)
    # 인덱스 추가됨
    post = fields.ForeignKeyField(
        "models.POSTS", related_name="post_tag_rels", index=True, source_field="post_id"
    )
    tag = fields.ForeignKeyField(
        "models.TAGS", related_name="tag_post_rels", source_field="tag_id"
    )

    class Meta:
        table = "POST_TAGS"

class BOOKMARKS(models.Model):
    bookmark_id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.USERS", source_field="user_id"
    )
    quote = fields.ForeignKeyField(
        "models.QUOTES", source_field="quote_id"
    )
    cdate = fields.DatetimeField(auto_now_add=True)

    class Meta:
        # 변수명인 user와 quote를 적어줍니다.
        unique_together = ("user", "quote")

class TOKEN_BLACKLIST(models.Model):
    blacklist_id = fields.IntField(pk=True)
    token = fields.CharField(max_length=500, unique=True)
    cdate = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField()

class QUOTES(models.Model):
    quote_id = fields.IntField(pk=True)
    contents = fields.CharField(max_length=500, unique=True)
    author = fields.CharField(max_length=100, null=True)
    cdate = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)

class REFLECTION_QUESTIONS(models.Model):
    question_id = fields.IntField(pk=True)
    contents = fields.CharField(max_length=500)
    cdate = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)
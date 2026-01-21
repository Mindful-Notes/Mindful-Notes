from tortoise import fields, models


class User(models.Model):
    user_id = fields.IntField(pk=True)
    user_email = fields.CharField(max_length=255, unique=True)
    hash_pass = fields.CharField(max_length=255)
    bookmark = fields.JSONField(default=list, description="명언 ID 리스트")
    cdate = fields.DatetimeField(auto_now_add=True, description="생성일")

    class Meta:
        table = "users"

class Post(models.Model):
    post_id = fields.IntField(pk=True)
    user_id = fields.ForeignKeyField('models.User', related_name='posts')
    title = fields.CharField(max_length=255)
    contents = fields.TextField()
    tag = fields.CharField(max_length=100, null=True)
    attached = fields.CharField(max_length=255, null=True)
    cdate = fields.DatetimeField(auto_now_add=True, description="생성일")

    class Meta:
        table = "posts"

class Quote(models.Model):
    quote_id = fields.IntField(pk=True)
    contents = fields.CharField(max_length=500)
    author = fields.CharField(max_length=100)
    is_active = fields.BooleanField(default=True)
    cdate = fields.DatetimeField(auto_now_add=True, description="생성일")

    class Meta:
        table = "quotes"

class ReflectionQuestion(models.Model):
    question_id = fields.IntField(pk=True)
    contents = fields.CharField(max_length=500)
    is_active = fields.BooleanField(default=True)
    cdate = fields.DatetimeField(auto_now_add=True, description="생성일")

    class Meta:
        table = "reflection_questions"
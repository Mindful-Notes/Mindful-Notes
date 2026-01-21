from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "quotes" (
    "quote_id" SERIAL NOT NULL PRIMARY KEY,
    "contents" VARCHAR(500) NOT NULL UNIQUE,
    "author" VARCHAR(100),
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL DEFAULT True
);
CREATE TABLE IF NOT EXISTS "reflection_questions" (
    "question_id" SERIAL NOT NULL PRIMARY KEY,
    "contents" VARCHAR(500) NOT NULL,
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL DEFAULT True
);
CREATE TABLE IF NOT EXISTS "tags" (
    "tag_id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "token_blacklist" (
    "blacklist_id" SERIAL NOT NULL PRIMARY KEY,
    "token" VARCHAR(500) NOT NULL UNIQUE,
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
    "user_id" SERIAL NOT NULL PRIMARY KEY,
    "user_email" VARCHAR(255) NOT NULL UNIQUE,
    "hashed_pass" VARCHAR(255) NOT NULL,
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "bookmarks" (
    "bookmark_id" SERIAL NOT NULL PRIMARY KEY,
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "quote_id" INT NOT NULL REFERENCES "quotes" ("quote_id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE,
    CONSTRAINT "uid_bookmarks_user_id_176fbb" UNIQUE ("user_id", "quote_id")
);
CREATE TABLE IF NOT EXISTS "posts" (
    "post_id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "contents" TEXT NOT NULL,
    "attached" VARCHAR(255),
    "status" VARCHAR(7) NOT NULL DEFAULT 'public',
    "deleted_date" TIMESTAMPTZ,
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_posts_status_061f42" ON "posts" ("status");
COMMENT ON COLUMN "posts"."status" IS 'PUBLIC: public\nDELETED: deleted';
CREATE TABLE IF NOT EXISTS "POST_TAGS" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "post_id" INT NOT NULL REFERENCES "posts" ("post_id") ON DELETE CASCADE,
    "tag_id" INT NOT NULL REFERENCES "tags" ("tag_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_POST_TAGS_post_id_4b119d" ON "POST_TAGS" ("post_id");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "Ua"
)

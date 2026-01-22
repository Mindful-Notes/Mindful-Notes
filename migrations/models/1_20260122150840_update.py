from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "tags" ADD "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        CREATE INDEX IF NOT EXISTS "idx_POST_TAGS_tag_id_8638ea" ON "POST_TAGS" ("tag_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_POST_TAGS_tag_id_8638ea";
        ALTER TABLE "tags" DROP COLUMN "cdate";"""


MODELS_STATE = (
    "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"
    "0FpLzV8w=="
)

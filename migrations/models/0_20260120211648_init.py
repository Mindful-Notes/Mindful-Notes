from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "quotes" (
    "quote_id" SERIAL NOT NULL PRIMARY KEY,
    "contents" VARCHAR(500) NOT NULL,
    "author" VARCHAR(100) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "quotes"."cdate" IS '생성일';
CREATE TABLE IF NOT EXISTS "reflection_questions" (
    "question_id" SERIAL NOT NULL PRIMARY KEY,
    "contents" VARCHAR(500) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "reflection_questions"."cdate" IS '생성일';
CREATE TABLE IF NOT EXISTS "users" (
    "user_id" SERIAL NOT NULL PRIMARY KEY,
    "user_email" VARCHAR(255) NOT NULL UNIQUE,
    "hash_pass" VARCHAR(255) NOT NULL,
    "bookmark" JSONB NOT NULL,
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "users"."bookmark" IS '명언 ID 리스트';
COMMENT ON COLUMN "users"."cdate" IS '생성일';
CREATE TABLE IF NOT EXISTS "posts" (
    "post_id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "contents" TEXT NOT NULL,
    "tag" VARCHAR(100),
    "attached" VARCHAR(255),
    "cdate" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id_id" INT NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE
);
COMMENT ON COLUMN "posts"."cdate" IS '생성일';
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
    "eJztmu9vmzgYx/8VxKtO2lVt1qzZaZqUtOkttzbZ2nRXdZuQAYdYMSYFszaa8r/fY/ObEB"
    "ZOYWl2vInC4+fB9gfbzxebH6rtmJh6hx8dj6t/Kj9UhmwMfzL2l4qK5vPEKgwc6VQ6zsFD"
    "WpDucRcZ4jYTRD0MJhN7hkvmnDgMrMynVBgdAxwJsxKTz8iDjzXuWJhPsQsFX76BmTATP2"
    "EvupzPtAnB1My0U1SvEVM0QBZqfDGXBQPGL6S3qFLXDIf6NstFzBd86rA4hDDZVwsz7CKO"
    "RUXc9UVHRDvDDkd9C9qcuASNTcWYeIJ8ylMd35CG4TBBElrjya5aopY/WscnpyedV69POu"
    "AiWxJbTpdBHxMAQaDEMByrS1mOOAo8JNCEICccbrfC72yK3GKAcUAOHzQ6jy+CVcYvMiQA"
    "k+GzJYI2etIoZhafCmztdgmvz93rs/fd6wPweiF648CQDgb6MCxqBWUCagIRauSYBRMhy3"
    "GMn9YMxHTMvqAsITfu341Fo23Pe6BpYAdX3TvJ0l6EJZej4V+Rewrw2eWol+PKkVVpaAbu"
    "/4lmOG13Ni6Pj442GJfgtXZcyrIsP8Q5Mqa4YH1cDzEds5ck65nhsIAWLJPnYOXExmumeB"
    "SU42iGUYfRn18629WvvnFkmvB7/OoYfk9PDXUzzC5G5ojRRfiQy1aDwVX/Zty9+phZEs67"
    "474oaWWWg8h68Dr3QOKbKP8Mxu8Vcancj4Z9SRTSuOXKGhO/8b0q2oR87mjMedSQmUrIkT"
    "UClXm8voddUAXVpEQ26Odq4nms4dsQFEKPTWaFeiKEsorxwnExsdgHvJA0B9AoxIyi6RGK"
    "z1u40/NEuIxGQmRNRpmLHmOZmhsg0EPoF+bB+tu9Oeue91WJUkfG7BG5ppZhKkqclpOzxL"
    "6rRXbLzlsQQ5ZEIDoimh2y/eQ7sh0rij8oKJX8D8Jlh5pf1l9tpqZDGtVfKljXC4N9FKxZ"
    "ZdDeSGO1SzRWu0Bj+YDCraSw4oj9xFiLVCWeBisJ+V4gsnqOQzFixTAzcTmeOgTWBTSe8N"
    "t+keqNRpcZ1dQb5N+Ubq96fQAs8YITCVJKNOsb0fobi9YV5bUb/XCNJxQb4tl88rEXPqMV"
    "MVHgVaos3NhfewgDdqozgiZUlRqZqEZtNGpjm2qjSZNNmmzS5L6kSbmFUZAYo62N9alQbB"
    "3sMPet3cX52WZYk/PSBLGNCK2S9bJR28l7tZOsf/d9irypNkdeJQWRCdpPCVELTEj3Mxu5"
    "s1WWf9+MhsUs0zE5lLcMuvjFJAZ/qVDi8W91gVXfTnwm3w4U3SeUE+YdigrfqUVpUEedNi"
    "TAtt5RBucKXL9BBly30MlX32zpnc3SYgl9Aav8wDN/tplLbeIG+QPPRor8n6VI9ruWgsWu"
    "F4ZdfLjGFEUv1MXHJ9G3O89vjVt3fLKsU4p1sUuMaZEYC0tK5RhKfHaixypJsUaFxdy+g4"
    "oOZ8mmsiEV0oiG5JQDpkYFiKH7fgKs5Xwj3M+qIrpSIbvSXLV9LrY19bTTN/3lv0Sv1ao="
)

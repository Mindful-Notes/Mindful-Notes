# 로그인 유저/DB 연결 같은 공통의존성 주입
# 역할: router에서 매번 반복할 것들 자동 주입. 로그인 유저 가져오기를 여기서 통일

from fastapi import Depends

from app.core.security import get_current_user


async def get_me(user = Depends(get_current_user)):
    return user

## DB는 Tortoise가 전역으로 연결되어 모델에서 바로 쿼리
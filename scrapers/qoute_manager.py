import asyncio

import httpx
from pydantic import ValidationError
from selectolax.parser import HTMLParser

from app.core.config import QuoteCreate, QuestionCreate
from app.core.database import close_db, init_db
from app.models import QUOTES, REFLECTION_QUESTIONS


class ContentScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }

    # 0. 페이지 가져오기
    async def get_html(self, url: str) -> HTMLParser:
        async with httpx.AsyncClient(
            headers=self.headers, timeout=30.0, follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return HTMLParser(response.text)

    # 1. 명언 스크래핑
    async def sync_quotes(self, max_sets: int = 10):
        base_url = "https://saramro.com/quotes"
        total_count = 0

        for set_idx in range(max_sets):
            start_page = (set_idx * 10) + 1
            end_page = start_page + 9
            print(
                f"\n[Next] {set_idx + 1}번째 묶음 수집 시작 ({start_page}p ~ {end_page}p)"
            )

            for page_num in range(start_page, end_page + 1):
                url = f"{base_url}?page={page_num}"

                try:
                    parser = await self.get_html(url)
                    nodes = parser.css(
                        "div.tbl_head01.tbl_wrap tbody tr:not([class]) td"
                    )

                    if not nodes:
                        print(f" {page_num}페이지에 데이터가 없습니다. 수집종료합니다.")
                        print(f" 최종 수집 개수: {total_count}개")
                        return

                    page_count = 0
                    for node in nodes:
                        raw_text = node.text().strip()
                        if not raw_text:
                            continue

                        parts = raw_text.rsplit("-")
                        content = parts[0].strip()
                        author = (" ".join(parts[1].strip().split()[:2]) if len(parts) >= 2 else "작자미상")

                        try:
                            quote_in = QuoteCreate(contents=content, author=author)
                            await QUOTES.get_or_create(
                                contents=quote_in.contents,
                                defaults={"author": quote_in.author},
                            )
                            page_count += 1
                        except ValidationError as e:
                            print(f"데이터 검증 에러(명언): {e}")
                            continue
                        except Exception as db_e:
                            print(f"DB 저장 에러(명언): {db_e}")
                            continue

                    total_count += page_count
                    print(f" ㄴ {page_num}페이지: {page_count}개 수집 완료")

                    # 페이지당 5초 딜레이 유지
                    await asyncio.sleep(5)

                except Exception as e:
                    print(f"{page_num}페이지 접속/파싱 에러 : {e}")
                    await asyncio.sleep(5)
                    continue

        print(f"\n {max_sets}세트 수집 완료 (총 {total_count}개)")

    # 2. 오늘의 질문 스크래핑
    async def sync_questions(self):
        base_url = "https://steemit.com/kr/@centering/1010"
        print(f"\n[Start] 질문 수집 시작: {base_url}")

        try:
            parser = await self.get_html(base_url)
            count = 0
            for node in parser.css(".MarkdownViewer.Markdown ol li"):
                raw_content = node.text().strip()
                if not raw_content:
                    continue

                try:
                    question_in = QuestionCreate(contents=raw_content)
                    await REFLECTION_QUESTIONS.get_or_create(
                        contents=question_in.contents
                    )
                    count += 1
                except ValidationError as e:
                    print(f"데이터 검증 에러: {e}")
                    continue
                except Exception as db_e:
                    print(f"DB 저장 에러: {db_e}")
                    continue

            print(f"오늘의 질문 {count}개 동기화 완료")
        except Exception as e:
            print(f"질문 수집 중 에러 발생 : {e}")


# 실행
async def run_all_scrapers():
    try:
        try:
            await init_db()
            print("oooooooo DB 연결 성공")
        except Exception as db_init_e:
            print(f"!!!!!!!! DB 연결 실패: {db_init_e}")
            return

        manager = ContentScraper()

        # 명언 수집
        await manager.sync_quotes()

        print("\n5초 대기중 .......")
        await asyncio.sleep(5)

        # 질문 수집
        await manager.sync_questions()

    except Exception as e:
        print(f"-------- 실행 중 오류 발생: {e}")
    finally:
        await close_db()
        print("xxxxxxxx DB 연결 종료")


if __name__ == "__main__":
    asyncio.run(run_all_scrapers())

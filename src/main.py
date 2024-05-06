import time
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from tqdm import tqdm
from src.limiter import Limiter
from src.config import AppSettings
from src.db_metadata import texts_table

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import URL
import logging
from src.log import conf_logger

conf_logger(logging.DEBUG)
sqlogger = logging.getLogger("sqlalchemy.engine")
sqlogger.setLevel(logging.WARNING)


articles_res_links = []
articles_res_texts = []
start_time = time.time()

baseUrl = "https://habr.com"


@Limiter(calls_limit=10, period=1)
async def get_articles_links(query_params, session, page):
    headers = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/,/*;q=0.8",
        "user-agent": "Mozilla/5.0",
    }

    url = f"https://habr.com/ru/search/page{page}?{query_params}"

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, "html.parser")

        articles_links = soup.find_all("a", class_="tm-article-snippet__readmore")

        for link in articles_links:
            articles_res_links.append(
                {
                    "link": f"{baseUrl}{link.get('href')}",
                }
            )

        print(f"Обработал страницу: {page}; url: {url}")


@Limiter(calls_limit=10, period=1)
async def get_article_texts(
    link, session, db_session_m: async_sessionmaker[AsyncSession], update_callback
):
    headers = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/,/*;q=0.8",
        "user-agent": "Mozilla/5.0",
    }

    async with session.get(url=link, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, "html.parser")

        body = soup.find("div", class_="article-formatted-body")

        if body is None:
            return
        text_inside_div = body.get_text(strip=True)

        async with db_session_m() as db_session:
            await db_session.execute(
                texts_table.insert().values(link=link, text=text_inside_div)
            )
            await db_session.commit()

    update_callback()


async def gather_pages():
    headers = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/,/*;q=0.8",
        "user-agent": "Mozilla/5.0",
    }

    params_list = [
        "q=CatBoost&target_type=posts&order=relevance",
        "q=PgPool2&target_type=posts&order=relevance",
        "q=Postgresql Explain&target_type=posts&order=relevance",
    ]
    async with aiohttp.ClientSession() as session:
        tasks = []
        for param in params_list:
            time.sleep(1)
            url = f"{baseUrl}/ru/search?{param}"
            response = await session.get(url=url, headers=headers)
            soup = BeautifulSoup(await response.text(), "html.parser")
            pages_el = soup.find_all("a", class_="tm-pagination__page")

            pages_count = 0
            for page_el in pages_el:
                tmp = int(page_el.text)
                if tmp > pages_count:
                    pages_count = tmp

            print(pages_count)

            for page in range(1, pages_count + 1):
                task = asyncio.create_task(get_articles_links(param, session, page))
                tasks.append(task)

            print(len(tasks))
            time.sleep(1)
        await asyncio.gather(*tasks)


async def gather_text_from_articles(db_session_maker: async_sessionmaker[AsyncSession]):
    async with aiohttp.ClientSession() as session:
        tasks = []
        print(f"Count links {len(articles_res_links)}")

        pbar = tqdm(total=len(articles_res_links))

        def update():
            pbar.update()

        for link in articles_res_links:
            task = asyncio.create_task(
                get_article_texts(link["link"], session, db_session_maker, update)
            )
            tasks.append(task)

        await asyncio.gather(*tasks)


async def main(config: AppSettings):
    url_object = URL.create(
        config.dialect,
        username=config.db_user,
        password=config.db_password.get_secret_value(),
        host=config.db_host,
        database=config.db_name,
        port=config.db_port,
    )

    engine = create_async_engine(url_object, echo=True)
    async_sessionm = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    await gather_pages()

    await gather_text_from_articles(async_sessionm)

    finish_time = time.time() - start_time
    print(f"Затраченное на работу скрипта время: {finish_time}")


if __name__ == "__main__":
    app_config = AppSettings()
    asyncio.run(main(app_config))

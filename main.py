import asyncio
import datetime
import os
import random
import json

import loguru
from fastapi import FastAPI, Request
from dynaconf import Dynaconf
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from func import fetch_page, write_json, get_hash_string, generate_secure_api_keys, write, get_date_now, write_photo_base64
from models import News, NewsList
from sites.autoru import AutoRu
from sites.base import BaseParser
from sites.gismetioBAD import Gismetio
from sites.interfax import Interfax
from sites.iz import IzRu, IzRuMariupol
from sites.kolesa import Kolesa
from sites.kommersant import Kommersant
from sites.newsdrom import NewsDrom
from sites.pogodamailru import PogodaMailRu
from sites.rbc import Rbc
from sites.rt import RT
from sites.ura import Ura
from sites.vesti import Vesti

app = FastAPI()
config = Dynaconf(settings_files=["config.toml"])
KEYS = generate_secure_api_keys(3, 444)

ACTUAL_NEWS = []
DATE_LAST = None
print("Актуальные ключи находятся в папке - keys")
[write(f'keys/{i}.txt', k) for i, k in enumerate(KEYS, start=1)]


class NewsParser:
    def __init__(self):
        self.categories = {
            "Политика": [IzRu("https://iz.ru/rubric/politika")],
            "Общество": [Rbc("https://www.rbc.ru/society/")],
            "Экономика": [Kommersant("https://www.kommersant.ru/rubric/3")],
            "Происшествия": [Vesti("https://www.vesti.ru/proisshestviya")],
            "Армия и оружие": [IzRu("https://iz.ru/rubric/armiia")],
            "В мире": [
                IzRu("https://iz.ru/rubric/mir"),
                Interfax("https://www.interfax.ru/world/"),
            ],
            "Мариуполь": [IzRuMariupol("https://iz.ru/tag/mariupol")],
            "Новороссия": [RT("https://russian.rt.com/tag/novorossiya")],
            "Развлечения": [
                Kommersant("https://www.kommersant.ru/theme/2317"),
                Ura("https://ura.news/rubrics/main/entertainment"),
                Rbc("https://www.rbc.ru/tags/?tag=развлечения"),
            ],
            "Природа": [IzRu("https://iz.ru/tag/priroda")],
        }

    async def run_parser(self):
        global DATE_LAST
        for category, urls in self.categories.items():
            for obj_pars in urls:
                await self.process_category(category, obj_pars)
                DATE_LAST = get_date_now()
                await asyncio.sleep(1)
        loguru.logger.success(f"Работа завершена. Sleep - {config.CIRCLE_TIME_MINUTES} minutes from the beginning parsing")


    async def process_category(self, category: str, object_parsing: BaseParser):
        soup = await fetch_page(object_parsing.url)
        result = await object_parsing.start(soup, category)

        if not result:
            loguru.logger.error(f"Не смог спарсить новость : {object_parsing.url}")
            return

        if result.photo_url:
            result.photo_base64 = await write_photo_base64(result.photo_url)

        if result not in ACTUAL_NEWS:
            ACTUAL_NEWS.append(result)
        loguru.logger.success(f"Сохранил : \n{result}")


@app.get("/parser/get_recent_news")
async def get_news(request: Request):
    news_list = []

    try:
        key = request.headers.get("Secure")
        if key not in KEYS:
            return {"error": "Нет доступа", "number": 2}

        if len(ACTUAL_NEWS) == 0:
            return {"error": "Новых актуальных новостей пока нет", "number": 1}

        for N in ACTUAL_NEWS:
            news_list.append(N.model_dump())
        ACTUAL_NEWS.clear()

        return NewsList(news=news_list, date=get_date_now(), secure="yes", number=3)
    except:
        return {"error": "Ошибка, проверьте правильность ваших данных", "number": 0}


async def main():
    parser = NewsParser()
    sch = AsyncIOScheduler()

    sch.add_job(
        func=parser.run_parser,
        trigger="interval",
        minutes=config.CIRCLE_TIME_MINUTES,
        next_run_time=datetime.datetime.now(),
    )

    sch.start()

    task1 = asyncio.create_task(parser.run_parser())
    task2 = asyncio.create_task(run_fastapi())

    await asyncio.gather(task1, task2)


async def run_fastapi():
    import uvicorn

    config = uvicorn.Config(app, port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())

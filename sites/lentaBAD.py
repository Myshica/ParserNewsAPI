from typing import Tuple, List

import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text
from models import News
from sites.base import BaseParser


class LentaRu(BaseParser):

    DEFAULT_URL = "https://lenta.ru"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url


    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        try:
            news_title = soup.find('div', class_='card-full-news__title').text.strip()
            news_url = self.DEFAULT_URL + soup.find('a', class_='card-full-news _subrubric').get('href')
            news_date = soup.find('time', class_='card-full-news__info-item card-full-news__date').text.strip()

            news_desc, news_photo = await self.open(news_url)
            new_news_desc = chat_gpt_change_text(news_desc)

            return News(title=news_title, desc=new_news_desc, date=news_date, photo_url=news_photo, category=cat)
        except Exception as e:
            loguru.logger.exception(f"Не смог распарсить {self.url}: {e}")

        return None


    async def open(self, other_url: str) -> tuple[str, str | list[str] | None] | tuple[None, None]:
        soup = await fetch_page(other_url)
        try:
            desc = soup.find("div", class_="topic-page__container").text.strip()
            photo = soup.find('img', class_="picture__image").get("src")
            return desc, photo
        except Exception as e:
            loguru.logger.error(f"На нашел на странице новости данные: {e}")
            return None, None




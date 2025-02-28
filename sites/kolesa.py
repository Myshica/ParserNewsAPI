from typing import Tuple, List

import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text, get_random_id, async_write
from models import News
from sites.base import BaseParser


class Kolesa(BaseParser):
    DEFAULT_URL = "https://www.kolesa.ru"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url

    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        news_title = None
        news_url = None
        news_date = None
        try:
            news_title = soup.find('span', class_='post-name').text.strip()
            try:
                news_url = self.DEFAULT_URL + soup.find('a', class_='post-list-item').get('href')
            except:
                pass
            news_desc, news_photo = await self.open(news_url)
            new_news_desc = chat_gpt_change_text(news_desc)
            return News(title=news_title, desc=new_news_desc, date=news_date, photo_url=news_photo, category=cat)
        except Exception as e:
            loguru.logger.exception(f"Не смог распарсить {self.url}: {e}")
            await async_write(str(soup))

        return None

    async def open(self, other_url: str) -> tuple[str, str | list[str] | None] | tuple[None, None]:
        soup = await fetch_page(other_url)
        try:
            desc = None
            try:
                desc = soup.find("div", class_="post-content").text.strip()
            except:
                pass

            soup.find()
            photo = soup.find('div', class_="gallery-image").find("img").get("src")
            return desc, photo
        except Exception as e:
            loguru.logger.exception(f"На нашел на странице новости данные: {e}")
            await async_write(str(soup))

        return None, None


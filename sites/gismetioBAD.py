
import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text, async_write
from models import News
from sites.base import BaseParser


class Gismetio(BaseParser):

    DEFAULT_URL = "https://www.gismeteo.ru"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url


    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        try:
            news_title = soup.find('div', class_='item-title').find('a').text.strip()
            news_url = self.DEFAULT_URL + soup.find('a', class_='article-item').get("href")
            news_date = soup.find('div', class_='item-date').text.strip()
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
            desc = soup.find("div", class_="item-text").text.strip()
            photo = soup.find("figure", "wp-block-image size-large").find("img").get("src")
            return desc, photo
        except Exception as e:
            print(soup)
            loguru.logger.error(f"На нашел на странице новости данные {other_url}: {e}")
            return None, None




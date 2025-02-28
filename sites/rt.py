import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text
from models import News
from sites.base import BaseParser


class RT(BaseParser):

    DEFAULT_URL = "https://russian.rt.com"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url


    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        try:
            news_title = soup.find('a', class_='link link_color').text.strip()
            news_url = self.DEFAULT_URL + soup.find('a', class_='link link_color').get("href")
            news_date = soup.find('time', class_='date').text.strip()
            news_desc, news_photo = await self.open(news_url)

            new_news_desc = chat_gpt_change_text(news_desc)

            return News(title=news_title, desc=new_news_desc, date=news_date, photo_url=news_photo, category=cat)
        except Exception as e:
            loguru.logger.exception(f"Не смог распарсить {self.url}: {e}")

        return None


    async def open(self, other_url: str) -> tuple[str, str | list[str] | None] | tuple[None, None]:
        soup = await fetch_page(other_url)
        try:
            desc = " ".join([i.text for i in soup.find("div", class_="article__text article__text_article-page js-mediator-article").find_all("p")])
            photo = soup.find("img", "article__cover-image").get("src")
            return desc, photo
        except Exception as e:
            loguru.logger.error(f"На нашел на странице новости данные {other_url}: {e}")
            return None, None




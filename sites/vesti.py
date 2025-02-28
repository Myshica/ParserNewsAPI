import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text
from models import News
from sites.base import BaseParser


class Vesti(BaseParser):

    DEFAULT_URL = "https://www.vesti.ru"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url


    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        try:
            news_title = soup.find('h3', class_='list__title').text.strip()
            news_url = self.DEFAULT_URL + soup.find('h3', class_='list__title').find("a").get("href")
            news_date = soup.find('div', class_='list__date').text.strip() + " " + soup.find('div', class_='list__time').text.strip()
            news_desc, news_photo = await self.open(news_url)

            new_news_desc = chat_gpt_change_text(news_desc)

            return News(title=news_title, desc=new_news_desc, date=news_date, photo_url=news_photo, category=cat)
        except Exception as e:
            loguru.logger.exception(f"Не смог распарсить {self.url}: {e}")

        return None


    async def open(self, other_url: str) -> tuple[str, str | list[str] | None] | tuple[None, None]:
        soup = await fetch_page(other_url)
        photo = None
        try:
            desc = soup.find("div", class_="js-mediator-article").text.strip()
            try:
                photo = soup.find("img", class_="vgtrk-lazy").get("data-src")
            except:
                pass
            return desc, photo
        except Exception as e:
            loguru.logger.error(f"На нашел на странице новости данные: {e}")
            return None, None




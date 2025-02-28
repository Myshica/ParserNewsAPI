import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text
from models import News
from sites.base import BaseParser


class PogodaMailRu(BaseParser):

    DEFAULT_URL = "https://pogoda.mail.ru/news/"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url


    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        try:
            news_title = soup.find('span', class_='newsitem__title-inner').text.strip()
            news_url = soup.find('a', class_='newsitem__title link-holder').get("href")
            news_date = soup.find('span', class_='newsitem__param js-ago').text.strip()
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
            desc = soup.find("main").text.strip()
            try:
                photo = soup.find("div", attrs={"article-item-type": "picture"}).find("img").get("src")
            except:
                pass
            return desc, photo
        except Exception as e:
            loguru.logger.error(f"На нашел на странице новости данные: {e}")
            return None, None




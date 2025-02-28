import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text, async_write
from models import News
from sites.base import BaseParser


class Interfax(BaseParser):

    DEFAULT_URL = "https://www.interfax.ru"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url


    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        # try:
        news_title = soup.find_all("div", class_="timeline__group")[0].find("div").text.strip()[5:]
        news_url = self.DEFAULT_URL + soup.find("div", class_="timeline__group").find("div").find("a").get("href")
        news_date = soup.find("div", class_="timeline__group").find("div").find("time").get("datetime")
        news_desc, news_photo = await self.open(news_url)

        new_news_desc = chat_gpt_change_text(news_desc)

        return News(title=news_title, desc=new_news_desc, date=news_date, photo_url=news_photo, category=cat)
        # except Exception as e:
        #     loguru.logger.error(f"Не смог распарсить {self.url}: {e}")
        #     await async_write(str(soup))

        return None


    async def open(self, other_url: str) -> tuple[str, str | list[str] | None] | tuple[None, None]:
        soup = await fetch_page(other_url)
        try:
            desc = None
            photo = None
            try:
                desc = [i.text.strip() for i in soup.find("article").find_all("p")]
            except:
                pass

            try:
                photo = soup.find("article").find("img").get("src")
            except:
                pass
            return desc, photo
        except Exception as e:
            loguru.logger.error(f"На нашел на странице новости данные {other_url}: {e}")
            await async_write(str(soup))

        return None, None




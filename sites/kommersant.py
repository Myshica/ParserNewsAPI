import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text, async_write, get_random_id
from models import News
from sites.base import BaseParser


class Kommersant(BaseParser):

    DEFAULT_URL = "https://www.kommersant.ru"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url


    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        try:
            news_title = soup.find('a', class_='uho__link uho__link--overlay').text.strip()
            news_url = self.DEFAULT_URL + soup.find('a', class_='uho__link uho__link--overlay').get('href')
            news_date = soup.find('p', class_='uho__tag rubric_lenta__item_tag hide_mobile').text.strip()
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
            # desc = "".join([i.text for i in soup.find_all("p", class_="doc__text")])
            photo = None
            desc = soup.find("div", class_="article_text_wrapper js-search-mark").text.strip()
            try:
                photo = soup.find("div", "photo").find('img', class_="doc_media__media js-lazyimage-source js-lazyimage-trigger").get("data-lazyimage-src")
            except:
                pass
            return desc, photo
        except Exception as e:
            loguru.logger.error(f"На нашел на странице новости данные {other_url}: {e}")
            await async_write(str(soup))
        return None, None




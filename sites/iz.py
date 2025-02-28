from typing import Tuple, List

import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text, get_random_id, async_write
from models import News
from sites.base import BaseParser


class IzRu(BaseParser):
    DEFAULT_URL = "https://iz.ru"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url

    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        news_title = None
        news_url = None
        news_date = None
        try:
            try:
                news_title = soup.find('div', class_='node__cart__item__inside__info__title small-title-style1').text.strip()
            except:
                try:
                    news_title = soup.find('h3', class_="tag-materials-item__title").text.strip()
                except:
                    pass

            try:
                news_url = self.DEFAULT_URL + soup.find('a', class_='node__cart__item__inside').get('href')
            except:
                try:
                    news_url = soup.find('a', class_='tag-materials-item').get('href')
                except:
                    pass

            try:
                news_date = soup.find('div', class_='node__cart__item__inside__info__time small-gray').text.strip()
            except:
                try:
                    news_date = soup.find('div', class_='tag-materials-item__date').text.strip()
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
                desc = soup.find("div", class_="text-article").text.strip()
            except:
                try:
                    desc = soup.find("div", class_="articleBody").text.strip()
                except:
                    pass
            photo = "https:" + soup.find('div', class_="big_photo__img").find("div").find("img").get("data-src")
            return desc, photo
        except Exception as e:
            loguru.logger.exception(f"На нашел на странице новости данные: {e}")
            await async_write(str(soup))

            return None, None


class IzRuMariupol(BaseParser):
    DEFAULT_URL = "https://iz.ru"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url

    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        try:
            news_title = soup.find('h3', class_='tag-materials-item__title').text.strip()
            news_url = soup.find('a', class_='tag-materials-item').get('href')
            news_date = soup.find('div', class_='tag-materials-item__date').text.strip()
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
            desc = soup.find("div", class_="text-article__inside").text.strip()
            photo = "https:" + soup.find('div', class_="big_photo__img").find("div").find("img").get("data-src")
            return desc, photo
        except Exception as e:
            loguru.logger.exception(f"На нашел на странице новости данные: {e}")
            await async_write(str(soup))

        return None, None

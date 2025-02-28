from typing import Tuple, List

import httpx
import loguru
from bs4 import BeautifulSoup

from func import fetch_page, chat_gpt_change_text, get_random_id, async_write, random_headers, write_json
from models import News
from sites.base import BaseParser


class Rbc(BaseParser):
    DEFAULT_URL = "https://rbc.ru"

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url
        self.cat = ""

    async def start(self, soup: BeautifulSoup, cat: str) -> List[News] | News | None:
        news_title = None
        news_url = None
        news_date = None

        self.cat = cat
        try:
            if "/tags/?tag=" in self.url:
                return await self._search_tag_request()
            else:
                try:
                    news_title = soup.find('span', class_='normal-wrap').text.strip()
                except:
                    pass
                try:
                    news_title = soup.find('span', class_='search-item__title').text.strip()
                except:
                    pass
                try:
                    news_url = soup.find('a', class_='item__link rm-cm-item-link js-rm-central-column-item-link').get('href')
                except:
                    pass
                try:
                    news_date = soup.find('span', class_='item__category').text.strip()
                except:
                    pass
                try:
                    news_date = " ".join(soup.find('span', class_='search-item__category').text.strip().split(", ")[2:])
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
            desc = soup.find("div", class_="article__text article__text_free").text.strip()
            photo = soup.find('img', class_="smart-image__img").get("src")
            return desc, None
        except Exception as e:
            loguru.logger.exception(f"На нашел на странице новости данные: {e}")
            await async_write(str(soup))

        return None, None

    async def _search_tag_request(self):
        cookies = {
            'splituid': 'uUjlbWaXj4U1o0YyA0WxAg==',
            '__rmid': 'kLy2xed6QAK3BqHkT-4wKA',
            'popmechanic_sbjs_migrations': 'popmechanic_1418474375998%3D1%7C%7C%7C1471519752600%3D1%7C%7C%7C1471519752605%3D1',
            'livetv-state': 'off',
            'mindboxDeviceUUID': '69cc0974-d6d4-4cea-b307-769d3c9e96c4',
            'directCrm-session': '%7B%22deviceGuid%22%3A%2269cc0974-d6d4-4cea-b307-769d3c9e96c4%22%7D',
            'js_d': 'false',
            '__rmsid': 'Zp4E9VsATVWMgJvNF5gQrQ',
            'qrator_msid2': 'v2.0.1737402391.674.5eb4193aIguY9LdT|MidFln7coyQZpCbZ|PfNLQu23SHn5Brled0FftC3ByCS93onPbLjbMXEbE3ZF/4I/g2CTg/wo20jjfFWylg5suLjrvhTerJjw7O5vGQ==-w9dTU50mh6kJ+dt/6HCFj9+8EUI=',
        }
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ru,en;q=0.9,de;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'dnt': '1',
            'sec-ch-ua': '"Chromium";v="130", "YaBrowser";v="24.12", "Not?A_Brand";v="99", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-gpc': '1',
        }

        params = {
            'tag': 'развлечения',
            'project': 'rbcnews',
            'page': '0',
        }
        client = httpx.AsyncClient()
        response = await client.get('https://www.rbc.ru/search/ajax/', params=params, cookies=cookies, headers=headers)
        data = response.json()
        if len(data.get("items")) > 0:
            news = data["items"][0]
            return News(title=news["title"], desc=news["body"], date=news["publish_date"], photo_url=news["picture"], category=self.cat)
        else:
            return None


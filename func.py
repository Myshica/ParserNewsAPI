import base64
import datetime
import hashlib
import json
import locale
import secrets
import string
import uuid

import aiofiles
import aiohttp
import httpx
import loguru
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from g4f import Client
from hashlib import sha256

import nest_asyncio

nest_asyncio.apply()


def random_headers():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru,en;q=0.9,de;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'adtech_uid=9bca0447-cce3-4fef-a72b-95c2bf1d29b2%3Alenta.ru; vpuid=1724930840.46-7188911500717513; _blocker_hidden=1; VARIANT=0; rchainid=%7B%22message%22%3A%22need%20session%22%2C%22code%22%3A-4000%2C%22details%22%3A%7B%22method%22%3A%22%2Fsession%2FgetRsidx%22%2C%22requestId%22%3A%22ridHnZHH5swxxG7yZnN1%22%7D%7D',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36',
        'dnt': '1',
        'sec-ch-ua': '"Chromium";v="130", "YaBrowser";v="24.12", "Not?A_Brand";v="99", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-gpc': '1',
    }
    headers = {"User-Agent": UserAgent().random}
    return headers


async def fetch_page(url: str) -> BeautifulSoup | None:
    try:
        async with httpx.AsyncClient(headers=random_headers(), timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        loguru.logger.error(f"Error fetching {url}: {e}")
        return None


def chat_gpt_change_text(text: str) -> None | str:
    result = None
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user",
                   "content": f"Уникализировать текст. Писать строго на русском языке. Не добавлять своих комментариев никаких! Не добавлять в результат ничего кроме результата. Убрать бессмысленные символы, сделать текст лучше, четче, правильнее. Убрать доменные имена из текста. Донести понятно главную мысль.\n{text}"}],
    )
    result = response.choices[0].message.content
    return result


def get_date_now():
    return datetime.datetime.now().replace(microsecond=0)


def get_random_id() -> str:
    return str(uuid.uuid4())


def get_hash_string(s: str):
    return hashlib.sha256(s.encode()).hexdigest()


def generate_secure_api_keys(count=5, length=40):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return [''.join(secrets.choice(alphabet).replace("#", "").replace('"', "") for _ in range(length)) for _ in range(count)]





async def write_photo_base64(url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Ошибка получения изображения для новости в запросе: {response.status} {response.reason}")

                image_bytes = await response.read()
                encoded = base64.b64encode(image_bytes).decode("utf-8")
                return encoded
    except Exception as e:
        loguru.logger.error(f"Ошибка получения фото: {url} | Подробности: {str(e)}")



def write_json(path, data) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def write(path, data) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(data)


async def async_write(data, path=f"error_pars_pages/{get_random_id()}.html") -> None:
    async with aiofiles.open(path, "w", encoding="utf-8") as file:
        await file.write(data)


def convert_date_flexible(date_str, output_format="%d.%m.%Y %H:%M") -> str:
    month = {"янв": "01", "фев": "02", "мар": "03", "апр": "04", "май": "05", "июн": "06", "июл": "07", "авг": "08", "сен": "09", "окт": "10", "ноя": "11", "дек": "12"}
    input_formats = [
        "%d/%m/%Y",  # Пример: "20/01/2025"
        "%d-%m-%Y",  # Пример: "20-01-2025"
        "%Y.%m.%d",  # Пример: "2025.01.20"
        "%B %d, %Y",  # Пример: "January 20, 2025"
        "%d %B %Y",  # Пример: "20 января 2025"
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 с временной зоной
        "%Y-%m-%dT%H:%M:%S",  # ISO 8601 без временной зоны
        "%d %B %Y, %H:%M",  # Пример: "20 января 2025, 17:26"
        "%Y-%m-%d %H:%M:%S",  # Пример: "2025-01-20 17:26:00"
        "%d.%m.%Y %H:%M",  # Пример: "20.01.2025 17:26"
        "%Y/%m/%d %H:%M",  # Пример: "2025/01/20 17:26"
        "%d.%m.%Y, %H:%M",  # Пример: 01.01.2025, 15:20,
        "%Y-%m-%dT%H:%M"  # Пример: 2025-01-21T15:39
    ]

    if "янв" in date_str:
        _date = date_str.split()
        month_numb = month[_date[1][:3]] if _date[1][:3] in month else None
        if month_numb:
            _date[2] = _date[2].replace(",", "")

            if len(_date) == 3:
                return f"{_date[0]}.{month_numb}.{_date[2]}"
            return f"{_date[0]}.{month_numb}.{_date[2]} {_date[3]}"

    if len(date_str) == 5:
        current_date = datetime.datetime.now().strftime(output_format)[:-6]
        return f'{current_date} {date_str}'

    for fmt in input_formats:
        try:
            date_obj = datetime.datetime.strptime(date_str, fmt)
            return date_obj.strftime(output_format)
        except ValueError:
            continue

    raise date_str

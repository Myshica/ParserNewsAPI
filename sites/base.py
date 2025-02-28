from bs4 import BeautifulSoup

from models import News


class BaseParser:
    DEFAULT_URL = ""

    def __init__(self, url: str):
        self.url = url

    async def start(self, soup: BeautifulSoup, cat: str) -> News | None:
        raise NotImplementedError("This method should be implemented in subclasses.")

    async def open(self, other_url: str) -> tuple[str, str | list[str] | None] | tuple[None, None]:
        raise NotImplementedError("This method should be implemented in subclasses.")
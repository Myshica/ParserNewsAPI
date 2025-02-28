from typing import Optional

import loguru
import pydantic
from pydantic import Field, validator, field_validator, BaseModel

from func import convert_date_flexible


class News(pydantic.BaseModel):
    title: str
    desc: str
    date: Optional[str | None] = None
    category: Optional[str | None] = None
    photo_url: Optional[str | None] = None
    photo_base64: Optional[str | None] = None


    @field_validator("date")
    def reformat_date(cls, value):
        try:
            return convert_date_flexible(value)
        except:
            loguru.logger.error(f"Не смог поменять дату {value} для: {cls.title} {cls.photo_url}")
            return None


    @field_validator("desc")
    def reformat_desc(cls, value):
        try:
            if "Free AI server, gpt-4o, claude-3.5-sonnet, o1," in value:
                return value.split("\n\n")[-1]
        except:
            loguru.logger.error(f"Не смог убрать их текста мусор {value} для: {cls.title} {cls.photo_url}")
            return None


class NewsList(BaseModel):
    news: list[News]
    date: str
    secure: str
    number: int


from datetime import datetime
from pydantic import BaseModel

from telegram.loader import config


class Datetime(BaseModel):
    year: str
    month: str
    day: str
    hour: str
    minute: str
    second: str

    @classmethod
    def from_datetime(cls, dt: datetime = None):
        if dt:
            return cls(
                year=dt.strftime("%Y"),
                month=dt.strftime("%m"),
                day=dt.strftime("%d"),
                hour=dt.strftime("%H"),
                minute=dt.strftime("%M"),
                second=dt.strftime("%S"),
            )
        return cls.from_datetime(datetime.now(config.TIMEZONE))

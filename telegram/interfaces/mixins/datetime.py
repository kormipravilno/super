from datetime import datetime
from pydantic import BaseModel, validator

from telegram.loader import config


class DateTimeMixin(BaseModel):
    dt: datetime = None

    @validator("dt", always=True)
    def validate_dt(cls, v):
        return v or datetime.now(config.TIMEZONE)

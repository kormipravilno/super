from pathlib import Path
from typing import Any, Optional, ClassVar
from pydantic import DirectoryPath, Field, validator

from telegram.loader import config
from telegram.interfaces.base import InternalBase
from telegram.interfaces.mixins import DateTimeMixin

from ...group import COURIER

DAILY_REPORT = COURIER.handler("daily_report", "Ежедневный отчет")


class DailyReportInternal(InternalBase, DateTimeMixin):
    key: ClassVar[str] = DAILY_REPORT.get_full_name("data")

    user_id: Optional[str] = Field(None, exclude=True)  # Only used for path
    path: Optional[DirectoryPath] = None
    data: dict[str, Any] = {}
    closed: bool = False

    @validator("path", always=True)
    def validate_path(cls, v, values: dict):
        if not v:
            if values["user_id"] is None:
                raise ValueError("user_id requiered if no path")
            v = Path(
                config.TMP_FOLDER,
                DAILY_REPORT.get_full_name(),
                values["dt"].strftime("%Y/%m/%d"),
                values["user_id"],
            )
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    def cleanup(self):
        return DailyReportInternal(
            dt=self.dt,
            path=self.path,
            closed=self.closed,
        )

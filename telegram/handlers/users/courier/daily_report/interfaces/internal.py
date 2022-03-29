from pathlib import Path
from typing import Any, Optional, ClassVar
from pydantic import DirectoryPath, Field, validator

from telegram.loader import config
from telegram.interfaces.base import InternalBase
from telegram.interfaces.mixins import DateTimeMixin

from ...group import COURIER

DAILY_REPORT = COURIER.handler("daily_report", "Ежедневный отчет")


class DailyReportInternalBase(InternalBase, DateTimeMixin):
    key: ClassVar[str] = DAILY_REPORT.get_full_name("data")

    closed: bool = False


class DailyReportInternal(DailyReportInternalBase):
    user_id: Optional[str] = Field(None, exclude=True)  # Only used for path
    path: Optional[Path] = None
    data: dict[str, Any] = {}

    @validator("path", always=True)
    def validate_path(cls, v, values: dict):
        if not v:
            if values["user_id"] is None:
                raise ValueError("user_id requiered if no path")
            v = Path(
                config.TMP_FOLDER,
                values["user_id"],
                DAILY_REPORT.get_full_name(),
                values["dt"].strftime("%Y/%m/%d"),
            )
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    def cleanup(self):
        return DailyReportInternal(
            dt=self.dt,
            path=self.path,
            closed=self.closed,
        )

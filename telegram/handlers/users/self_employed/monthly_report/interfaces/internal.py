from datetime import date
from pathlib import Path
import shutil
from typing import Any, Optional, ClassVar, Union
from pydantic import BaseModel, DirectoryPath, Field, validator
import aiogram.types

from common.schemas import SEServiceGet, ContentType

from telegram.loader import config, dp
from telegram.interfaces.base import InternalBase
from telegram.interfaces.mixins import DateTimeMixin, CurrentMessageMixin

from ...group import SELF_EMPLOYED

MONTHLY_REPORT = SELF_EMPLOYED.handler("monthly_report", "Ежемесячный отчет")


class Service(SEServiceGet):
    value: Union[Path, int, bool]
    amount: int
    payout: float

    @staticmethod
    def amount_from_value(value: Union[Path, int, bool]):
        if isinstance(value, Path):
            amount = 0
            for path in Path(value).iterdir():
                if path.is_file():
                    amount += 1
        elif isinstance(value, bool):
            amount = int(value)
        elif isinstance(value, int):
            amount = value
        return amount

    @classmethod
    def from_value(cls, service: SEServiceGet, value: Union[Path, int, bool]):
        amount = cls.amount_from_value(value)
        payout = amount * service.cost
        return cls(**service.dict(), value=value, amount=amount, payout=payout)


class MRInternalBase(InternalBase, DateTimeMixin):
    key: ClassVar[str] = MONTHLY_REPORT.get_full_name("data")

    closed: bool = False

    def to_closed(self) -> "MRClosedInternal":
        return MRClosedInternal(dt=self.dt, closed=True)


class MRInternal(MRInternalBase, CurrentMessageMixin):
    user_id: Optional[str] = Field(None, exclude=True)  # Only used for path
    path: Path = None
    services: list[Service] = []

    # TODO move in own class
    current_service: Optional[SEServiceGet] = None

    @validator("path", always=True)
    def validate_path(cls, v, values: dict):
        if not v:
            if values["user_id"] is None:
                raise ValueError("user_id requiered if no path")
            v = Path(
                config.TMP_FOLDER,
                values["user_id"],
                MONTHLY_REPORT.get_full_name(),
                values["dt"].strftime("%Y/%m"),
            )
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    def get_service(self, id):
        for service in self.services:
            if service.id == id:
                return service

    def delete_service(self, service: Service):
        self.services.remove(service)
        if isinstance(service.value, Path):
            if service.value.exists():
                shutil.rmtree(service.value)

    def cleanup(self):
        if self.path.exists():
            shutil.rmtree(self.path)

    def to_uploaded(self, folder_id: str) -> "MRUploadedInternal":
        return MRUploadedInternal(dt=self.dt, path=self.path, folder_id=folder_id)


class MRUploadedInternal(MRInternalBase):
    folder_id: str
    path: DirectoryPath

    def to_official(self, receipt_until: date) -> "MROfficialInternal":
        return MROfficialInternal(**self.dict(), receipt_until=receipt_until)


class MROfficialInternal(MRUploadedInternal):
    receipt_until: date


class MRClosedInternal(MRInternalBase):
    closed: bool = True

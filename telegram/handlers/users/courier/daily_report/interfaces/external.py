from typing import Literal, Optional
from pydantic import BaseModel, HttpUrl

from common.schemas import CourierSchema
from telegram.interfaces import Datetime
from telegram.interfaces.base import ExternalBase

from .internal import DailyReportInternal


class DailyReportExternalData(BaseModel):
    is_submitted: str = "Да"
    mileage_init: int
    odometer: HttpUrl
    shift_opened: bool
    orders: int
    orders_noreceipt: Optional[str] = None
    mileage_final: int
    proceeds: int
    proceeds_cash: int
    cash_noreceipt: int
    cash_atm: float
    cash_cardtocard: float
    atm_receipt: HttpUrl
    cardtocard_receipt: Optional[HttpUrl] = None


class DailyReportExternal(ExternalBase):
    data: DailyReportExternalData
    courier: CourierSchema
    dt_start: Datetime
    dt_end: Datetime
    NULL: Literal["NULL"] = "NULL"

    @classmethod
    def from_internal(cls, internal: DailyReportInternal, courier: CourierSchema):
        return cls(
            data=internal.data,
            courier=courier,
            dt_start=Datetime.from_datetime(internal.dt),
            dt_end=Datetime.from_datetime(),
        )

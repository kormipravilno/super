from typing import Union
from pydantic import HttpUrl
from common._schemas.users.self_employed import SelfEmployedGet

from telegram.interfaces.mixins import DateTimeMixin
from telegram.interfaces.base import ExternalBase
from telegram.interfaces import Datetime

from .internal import Service
from .info import Info


class ServiceExternal(ExternalBase, Service):
    value: Union[HttpUrl, int, bool]

    @classmethod
    def from_internal(
        cls, internal: Service, value: Union[HttpUrl, int, bool]
    ) -> "ServiceExternal":
        return cls(**internal.dict() | {"value": value})


class MonthlyReportExternal(ExternalBase):
    dt_start: Datetime
    dt_end: Datetime
    self_employed: SelfEmployedGet
    services: list[ServiceExternal]
    url: HttpUrl
    info: Info

    def get_service(self, id):
        for service in self.services:
            if service.id == id:
                return service

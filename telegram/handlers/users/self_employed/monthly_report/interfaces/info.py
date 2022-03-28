from typing import Generic, TypeVar
from pydantic.generics import GenericModel
from pydantic import BaseModel

from common.schemas import ContentType

from .internal import Service


T = TypeVar("T", str, float)


class Property(GenericModel, Generic[T]):
    total: T
    no_photos: T


class Info(BaseModel):
    payout: Property[float]
    text: Property[str]

    @classmethod
    def from_services(cls, services: list[Service]) -> "Info":
        self = cls(
            payout=Property(total=0, no_photos=0),
            text=Property(total="", no_photos=""),
        )
        for service in services:
            self.payout.total += service.payout
            self.text.total += f"{service.name} - {service.value}\n"
            if service.type != ContentType.PHOTOS:
                self.payout.no_photos += service.payout
                self.text.no_photos += f"{service.name} - {service.value}\n"

        if self.text.total == "":
            self.text.total = "—"
        else:
            self.text.total = self.text.total[:-1]
        if self.text.no_photos == "":
            self.text.no_photos = "—"
        else:
            self.text.no_photos = self.text.no_photos[:-1]
        return self

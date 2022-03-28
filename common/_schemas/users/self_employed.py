from typing import Optional

from common._schemas.services import SEServiceGet
from .common import UserSchema


class SelfEmployedSchema(UserSchema):
    template_id: Optional[str] = None
    passport: Optional[str] = None
    itn: Optional[str] = None
    contract_number: Optional[str] = None
    contract_date: Optional[str] = None


class SelfEmployedGet(SelfEmployedSchema):
    services: list[SEServiceGet]

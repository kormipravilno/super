from typing import Optional
from pydantic import validator

from .common import UserSchema


class CourierSchema(UserSchema):
    city: str
    sheet_name: str
    folder_id: str
    is_gsm: bool
    gsm_cost: float
    gsm_rate: float
    is_to: bool
    to_cost: Optional[float] = None
    shift_cost: Optional[float] = None

    @validator("is_gsm", "is_to", pre=True)
    def validate_is(cls, v):
        if isinstance(v, bool):
            return v
        if v == "TRUE":
            return True
        if v == "FALSE":
            return False
        raise ValueError('Must be either boolean or "TRUE" or "FALSE"')

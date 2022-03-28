from typing import Optional
from pydantic import validator

from common.base_model import PropertyBaseModel


class UserSchema(PropertyBaseModel):
    id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None

    @validator("id")
    def validate_id(cls, v):
        if not (v > 0):
            raise ValueError("must be a positive integer")
        return v

    @property
    def initials(self):
        initials = ""
        if self.last_name:
            initials += self.last_name + " "
        initials += self.first_name[0] + "."
        if self.middle_name:
            initials += self.middle_name[0] + "."
        return initials

    @property
    def full_name(self):
        full_name = ""
        if self.last_name:
            full_name += self.last_name + " "
        full_name += self.first_name + " "
        if self.middle_name:
            full_name += self.middle_name

        if full_name[-1] == " ":
            full_name = full_name[:-1]
        return full_name

    class Config:
        orm_mode = True

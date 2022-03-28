from pydantic import BaseModel

from common._schemas.types import ContentType


class SEServiceSchema(BaseModel):
    name: str
    type: ContentType
    cost: float

    self_employed_id: int

    class Config:
        orm_mode = True


class SEServiceGet(SEServiceSchema):
    id: int

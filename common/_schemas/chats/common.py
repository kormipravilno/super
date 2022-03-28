from pydantic import validator, BaseModel


class ChatSchema(BaseModel):
    id: int
    name: str

    @validator("id")
    def validate_id(cls, v):
        if not (v < 0):
            raise ValueError("must be a negative integer")
        return v

    class Config:
        orm_mode = True

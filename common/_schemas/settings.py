from pydantic import BaseModel


class SettingsSchema(BaseModel):
    key: str
    value: str

    class Config:
        orm_mode = True

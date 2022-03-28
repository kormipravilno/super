from pathlib import Path
from pydantic import BaseModel, validator, DirectoryPath


class PathMixin(BaseModel):
    path: DirectoryPath

    @validator("path", pre=True)
    def validate_dt(cls, v):
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

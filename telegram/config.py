from pydantic import DirectoryPath, RedisDsn, validator
from datetime import tzinfo
from pytz import timezone
from pathlib import Path

from common.config import BaseConfig


class Config(BaseConfig):
    REDISTOGO_URL: RedisDsn
    TELEGRAM: str
    TIMEZONE: tzinfo
    SPREADSHEET: str
    TMP_FOLDER: DirectoryPath = None

    @validator("TIMEZONE", pre=True)
    def timezone_validator(cls, v):
        return timezone(v)

    @validator("TMP_FOLDER", pre=True)
    def tmp_folder_validator(cls, v):
        if not v:
            v = Path("tmp").resolve()
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

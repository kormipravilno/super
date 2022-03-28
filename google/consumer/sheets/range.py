from google.api import SheetsRange
from .group import SHEETS

RANGE = SHEETS.group("range")


@RANGE.worker()
async def init(
    *,
    name: str = "",
    col_start: str = "",
    row_start: str = "",
    col_end: str = "",
    row_end: str = ""
) -> SheetsRange:
    return SheetsRange(name, col_start, row_start, col_end=col_end, row_end=row_end)


@RANGE.worker()
async def call(*, range: SheetsRange) -> str:
    return range()

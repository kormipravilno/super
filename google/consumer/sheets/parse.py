from google.api import SheetsParser
from .group import SHEETS

PARSE = SHEETS.group("parse")


@PARSE.worker("spreadsheet")
async def spreadsheet(*, data: dict):
    return SheetsParser.spreadsheet(data)


@PARSE.worker("table")
async def table(*, tag: str, rows: list[list]):
    return SheetsParser.table(tag, rows)

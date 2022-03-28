from typing import Any

from google.loader import client
from google.api import Sheets, SheetsRange, SheetsParser

from .group import SHEETS

PROCESS = SHEETS.group("process")


@PROCESS.worker()
async def get(*, id):
    async with client as c:
        sheets = Sheets(c)
        return await sheets.get(id)


@PROCESS.worker()
async def get_sheet_schema(*, id, sheet_name) -> list[Any]:
    range = SheetsRange(sheet_name, "", "1")
    async with client as c:
        sheets = Sheets(c)
        response = await sheets.values_get(id, range())
    return response["values"][0]


@PROCESS.worker()
async def get_values(*, id, range: str):

    async with client as c:
        sheets = Sheets(c)
        return await sheets.values_get(id, range)


@PROCESS.worker()
async def get_values_by_metadata(*, id, key, value):
    async with client as c:
        sheets = Sheets(c)

        matched_value_range = await sheets.values_get_by_metadata(id, key, value)
        if matched_value_range["valueRanges"]:
            return await sheets.values_get(
                id, matched_value_range["valueRanges"][0]["valueRange"]["range"]
            )


@PROCESS.worker()
async def append(*, id, sheet_name, values: list[list]) -> str:
    range = SheetsRange(sheet_name)
    async with client as c:
        sheets = Sheets(c)
        append_response = await sheets.values_append(id, range, values)
        row = SheetsParser.appended_row(append_response)
        range = SheetsRange(sheet_name, "", str(row))
        return await sheets.values_get(id, range())

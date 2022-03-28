from itertools import zip_longest
from pprint import pprint
from typing import Any
from logging import getLogger

from .common import Service

logger = getLogger(__name__)


class SheetsRange:
    """
    Good enough range parser.
    """

    def __init__(
        self,
        name: str = "",
        col_start: str = "",
        row_start: str = "",
        /,
        col_end: str = "",
        row_end: str = "",
    ) -> None:
        if not (name or row_start or col_start):
            raise ValueError("Either name, row_start or col_start is required")

        self.name = name
        self.col_start = col_start
        self.row_start = row_start
        self.col_end = col_end
        self.row_end = row_end

    def __call__(self):
        range = ""

        if self.name:
            range += self.name + "!"

        if self.col_start or self.row_start:
            range += self.col_start + self.row_start + ":"

        if self.col_end or self.row_end:
            range += self.col_end + self.row_end
        else:
            range += self.col_start + self.row_start

        return range


class Sheets(Service, api_name="sheets", api_version="v4"):
    async def get(self, id):
        logger.info(f"Getting {id}...")
        return await self.client.as_service_account(
            self.API.spreadsheets.get(
                spreadsheetId=id,
                fields="sheets.data.rowData.values.formattedValue,"
                "sheets.properties.title,"
                "sheets.properties.sheetId,"
                "sheets.merges,"
                "spreadsheetId",
            )
        )

    async def batch_update(self, id, requests: list):
        logger.info(f"Batch updating {id}...")
        return await self.client.as_service_account(
            self.API.spreadsheets.batchUpdate(
                spreadsheetId=id, json={"requests": requests}
            )
        )

    async def values_get_by_metadata(self, id, key: str, value: str):
        return await self.client.as_service_account(
            self.API.spreadsheets.values.batchGetByDataFilter(
                spreadsheetId=id,
                json={
                    "dataFilters": [
                        {
                            "developerMetadataLookup": {
                                "metadataKey": key,
                                "metadataValue": value,
                            }
                        }
                    ],
                    "valueRenderOption": "FORMATTED_VALUE",
                    "majorDimension": "ROWS",
                },
            )
        )

    async def values_get(self, id, range: str):
        logger.info(f"Getting {range} from {id}...")
        return await self.client.as_service_account(
            self.API.spreadsheets.values.get(spreadsheetId=id, range=range)
        )

    async def values_append(self, id, range: SheetsRange, values: list[list[Any]]):
        logger.info(f"Appending to {range.name} from {id}...")
        return await self.client.as_service_account(
            self.API.spreadsheets.values.append(
                spreadsheetId=id,
                range=range.name,
                valueInputOption="RAW",
                insertDataOption="OVERWRITE",
                includeValuesInResponse=False,
                json={"values": values},
            )
        )

    async def values_update(self, id, range: SheetsRange, values: list[list[Any]]):
        logger.info(f"Updating {range()} from {id}...")
        return await self.client.as_service_account(
            self.API.spreadsheets.values.update(
                spreadsheetId=id,
                range=range(),
                valueInputOption="RAW",
                json={"values": values},
            )
        )

    @staticmethod
    def create_developer_data(sheet_id: int, row: int, key: str, value: str):
        return {
            "createDeveloperMetadata": {
                "developerMetadata": {
                    "metadataKey": key,
                    "metadataValue": value,
                    "location": {
                        "dimensionRange": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": row,
                            "endIndex": row + 1,
                        }
                    },
                    "visibility": "DOCUMENT",
                }
            }
        }


class SheetsParser:
    MERGED = 0

    @staticmethod
    def spreadsheet(response: dict) -> dict:
        result = {}
        for sheet in response["sheets"]:
            values = []
            sheet_data = sheet["data"][0]
            for i_row, row in enumerate(sheet_data.get("rowData", [])):
                if "values" in row:
                    rowdata = []
                    for i_cell, cell in enumerate(row["values"]):
                        if "formattedValue" in cell:
                            rowdata.append(cell["formattedValue"])
                        else:
                            if "merges" in sheet and SheetsParser.__is_merged(
                                sheet["merges"], i_row, i_cell
                            ):
                                rowdata.append(SheetsParser.MERGED)
                            else:
                                rowdata.append("")
                    values.append(rowdata)
            result[sheet["properties"]["title"]] = values
        return result

    @staticmethod
    def __is_merged(merges: list[dict], i_row: int, i_cell: int):
        for merge in merges:
            row = (merge["startRowIndex"], merge["endRowIndex"])
            column = (merge["startColumnIndex"], merge["endColumnIndex"])
            if i_row in range(row[0], row[1]) and i_cell in range(column[0], column[1]):
                return True
        return False

    @staticmethod
    def table(tag: str, rows: list[list]):
        start_index = rows.index([f"{{{tag}}}"])
        end_index = rows.index([f"{{/{tag}}}"])
        table = rows[start_index + 1 : end_index]

        columns = table[0]
        table = table[2:]

        parsed = []
        for row in table:
            parsed.append(dict(zip_longest(columns, row, fillvalue=None)))
        return parsed

    @staticmethod
    def appended_row(data: dict) -> int:
        row = ""
        for char in data["updates"]["updatedRange"][::-1]:
            if char.isdigit():
                row += char
            else:
                break
        row = int(row[::-1])
        return row

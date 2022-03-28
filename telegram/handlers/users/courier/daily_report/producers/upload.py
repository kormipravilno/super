from pprint import pprint
from typing import Any
from pathlib import Path

from common.schemas import CourierSchema
from common.mq.engine import rpc
from common.crud import settings

from ..interfaces import DailyReportExternal


async def upload_files(
    data: dict[str, Any],
    courier: CourierSchema,
) -> dict[str, str]:
    files = {name: value for name, value in data.items() if isinstance(value, Path)}
    print(files)

    data_uploaded: dict[str, dict[str, Any]] = await rpc.call(
        "google.drive.upload_all",
        dict(
            files=files,
            parent_id=courier.folder_id,
        ),
    )
    for name, response in data_uploaded.items():
        data_uploaded[name] = response.get("webViewLink")

    return data_uploaded


async def upload_data(external: DailyReportExternal):
    spreadsheet = await settings.get("spreadsheet_data")
    schema = await rpc.call(
        "google.sheets.process.get_sheet_schema",
        dict(
            id=spreadsheet,
            sheet_name=external.courier.sheet_name,
        ),
    )

    data = external.to_flat_dict(preserve_special=True)
    values = []
    for key in schema:
        values.append(data.get(key))

    pprint(data)

    record_data = await rpc.call(
        "google.sheets.process.append",
        dict(
            id=spreadsheet,
            sheet_name=external.courier.sheet_name,
            values=[values],
        ),
    )

    record = dict(zip(schema, record_data["values"][0]))
    return record


def get_row(data: dict):
    row = ""
    for char in data["updates"]["updatedRange"][::-1]:
        if char.isdigit():
            row += char
        else:
            break
    row = int(row[::-1])
    return row
